from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import shutil
import uuid
from datetime import datetime

from config import settings
from models import (
    ChatRequest, ChatResponse, Message, MessageRole,
    DocumentUploadResponse, Conversation,
    MindMapRequest, MindMapResponse,
    NoteRequest, Note,
    QuizRequest, QuizResponse
)
from document_processor import DocumentProcessor
from vector_store import VectorStore
from chat_service import ChatService
from mindmap_service import MindMapService
from note_service import NoteService
from quiz_service import QuizService

# Initialize FastAPI app
app = FastAPI(
    title="Math Chatbot API",
    description="API cho chatbot hỗ trợ học sinh cấp 3 học toán",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
document_processor = DocumentProcessor()
vector_store = VectorStore()
chat_service = ChatService()
mindmap_service = MindMapService()
note_service = NoteService()
quiz_service = QuizService()

# In-memory storage (trong production nên dùng database thực)
conversations_storage = {}
documents_storage = {}

# ==================== HEALTH CHECK ====================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Math Chatbot API is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "gemini_api": "connected",
            "vector_store": "active",
            "document_storage": "active"
        }
    }

# ==================== DOCUMENT MANAGEMENT ====================

@app.post("/api/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload và xử lý tài liệu"""
    try:
        # Kiểm tra kích thước file
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File quá lớn. Kích thước tối đa: {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
            )
        
        # Reset file pointer
        await file.seek(0)
        
        # Lưu file tạm thời
        file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Xử lý document
        doc_data = await document_processor.process_document(file_path, file.filename)
        
        # Lưu vào storage
        documents_storage[doc_data["id"]] = doc_data
        
        # Chunk và thêm vào vector store
        chunks = document_processor.chunk_text(doc_data["content"])
        vector_store.add_document(
            doc_id=doc_data["id"],
            content=doc_data["content"],
            metadata={
                "filename": doc_data["filename"],
                "file_type": doc_data["file_type"]
            },
            chunks=chunks
        )
        
        return DocumentUploadResponse(
            document_id=doc_data["id"],
            filename=doc_data["filename"],
            status="success",
            message="Tải tài liệu thành công"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý tài liệu: {str(e)}")

@app.get("/api/documents")
async def get_documents():
    """Lấy danh sách tất cả tài liệu"""
    try:
        docs = [
            {
                "id": doc["id"],
                "filename": doc["filename"],
                "file_type": doc["file_type"],
                "upload_date": doc.get("upload_date", datetime.now()).isoformat()
            }
            for doc in documents_storage.values()
        ]
        return {"documents": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents/{document_id}")
async def get_document(document_id: str):
    """Lấy thông tin chi tiết của một tài liệu"""
    if document_id not in documents_storage:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu")
    
    doc = documents_storage[document_id]
    return {
        "id": doc["id"],
        "filename": doc["filename"],
        "file_type": doc["file_type"],
        "content": doc["content"][:500] + "..." if len(doc["content"]) > 500 else doc["content"],
        "metadata": doc.get("metadata", {})
    }

@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    """Xóa tài liệu"""
    if document_id not in documents_storage:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu")
    
    # Xóa khỏi vector store
    vector_store.delete_document(document_id)
    
    # Xóa khỏi storage
    del documents_storage[document_id]
    
    return {"message": "Xóa tài liệu thành công"}

# ==================== CHAT ====================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat với AI"""
    try:
        # Lấy hoặc tạo conversation
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        if conversation_id not in conversations_storage:
            conversations_storage[conversation_id] = Conversation(
                id=conversation_id,
                title=request.message[:50],
                messages=[],
                document_ids=request.document_ids or []
            )
        
        conversation = conversations_storage[conversation_id]
        
        # Thêm tin nhắn của user
        user_message = Message(
            role=MessageRole.USER,
            content=request.message
        )
        conversation.messages.append(user_message)
        
        # Gọi chat service
        response_data = await chat_service.chat(
            message=request.message,
            conversation_history=conversation.messages,
            document_ids=request.document_ids
        )
        
        # Thêm response vào conversation
        assistant_message = Message(
            role=MessageRole.ASSISTANT,
            content=response_data["response"]
        )
        conversation.messages.append(assistant_message)
        conversation.updated_at = datetime.now()
        
        return ChatResponse(
            response=response_data["response"],
            conversation_id=conversation_id,
            sources=response_data.get("sources", [])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi chat: {str(e)}")

@app.get("/api/conversations")
async def get_conversations():
    """Lấy danh sách hội thoại"""
    convs = [
        {
            "id": conv.id,
            "title": conv.title,
            "message_count": len(conv.messages),
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.updated_at.isoformat()
        }
        for conv in conversations_storage.values()
    ]
    return {"conversations": convs}

@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Lấy chi tiết một hội thoại"""
    if conversation_id not in conversations_storage:
        raise HTTPException(status_code=404, detail="Không tìm thấy hội thoại")
    
    return conversations_storage[conversation_id]

@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Xóa hội thoại"""
    if conversation_id not in conversations_storage:
        raise HTTPException(status_code=404, detail="Không tìm thấy hội thoại")
    
    del conversations_storage[conversation_id]
    return {"message": "Xóa hội thoại thành công"}

# ==================== MINDMAP ====================

@app.post("/api/mindmap", response_model=MindMapResponse)
async def create_mindmap(request: MindMapRequest):
    """Tạo mind map"""
    try:
        root_node = await mindmap_service.generate_mindmap(
            topic=request.topic,
            document_ids=request.document_ids,
            depth=request.depth
        )
        
        return MindMapResponse(
            root_node=root_node,
            topic=request.topic
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tạo mindmap: {str(e)}")

@app.post("/api/concept-map")
async def create_concept_map(concepts: List[str], document_ids: Optional[List[str]] = None):
    """Tạo concept map liên kết các khái niệm"""
    try:
        concept_map = await mindmap_service.generate_concept_map(
            concepts=concepts,
            document_ids=document_ids
        )
        return concept_map
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tạo concept map: {str(e)}")

# ==================== NOTES ====================

@app.post("/api/notes", response_model=Note)
async def create_note(request: NoteRequest):
    """Tạo ghi chú mới"""
    try:
        note = await note_service.create_note(
            title=request.title,
            content=request.content,
            document_ids=request.document_ids,
            auto_generate=request.auto_generate
        )
        return note
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tạo ghi chú: {str(e)}")

@app.get("/api/notes")
async def get_notes():
    """Lấy tất cả ghi chú"""
    try:
        notes = note_service.get_all_notes()
        return {"notes": notes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/notes/{note_id}", response_model=Note)
async def get_note(note_id: str):
    """Lấy chi tiết ghi chú"""
    note = note_service.get_note(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Không tìm thấy ghi chú")
    return note

@app.put("/api/notes/{note_id}", response_model=Note)
async def update_note(note_id: str, title: Optional[str] = None, content: Optional[str] = None):
    """Cập nhật ghi chú"""
    note = await note_service.update_note(note_id, title, content)
    if not note:
        raise HTTPException(status_code=404, detail="Không tìm thấy ghi chú")
    return note

@app.delete("/api/notes/{note_id}")
async def delete_note(note_id: str):
    """Xóa ghi chú"""
    success = note_service.delete_note(note_id)
    if not success:
        raise HTTPException(status_code=404, detail="Không tìm thấy ghi chú")
    return {"message": "Xóa ghi chú thành công"}

@app.post("/api/notes/summarize")
async def summarize_notes(note_ids: List[str]):
    """Tóm tắt nhiều ghi chú"""
    try:
        summary = await note_service.summarize_notes(note_ids)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/notes/{note_id}/flashcards")
async def get_flashcards(note_id: str):
    """Tạo flashcards từ ghi chú"""
    try:
        flashcards = await note_service.generate_flashcards(note_id)
        return {"flashcards": flashcards}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== QUIZ ====================

@app.post("/api/quiz", response_model=QuizResponse)
async def create_quiz(request: QuizRequest):
    """Tạo bài quiz"""
    try:
        questions = await quiz_service.generate_quiz(
            topic=request.topic,
            num_questions=request.num_questions,
            difficulty=request.difficulty,
            document_ids=request.document_ids
        )
        
        return QuizResponse(
            questions=questions,
            topic=request.topic
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tạo quiz: {str(e)}")

@app.post("/api/practice-problems")
async def create_practice_problems(
    topic: str,
    num_problems: int = 5,
    difficulty: str = "medium",
    document_ids: Optional[List[str]] = None
):
    """Tạo bài tập tự luận"""
    try:
        problems = await quiz_service.generate_practice_problems(
            topic=topic,
            num_problems=num_problems,
            difficulty=difficulty,
            document_ids=document_ids
        )
        return {"problems": problems}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/check-answer")
async def check_answer(question: str, user_answer: str, correct_answer: str):
    """Kiểm tra câu trả lời"""
    try:
        result = await quiz_service.check_answer(question, user_answer, correct_answer)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== UTILITY ENDPOINTS ====================

@app.post("/api/study-plan")
async def create_study_plan(topic: str, document_ids: Optional[List[str]] = None):
    """Tạo kế hoạch học tập"""
    try:
        plan = await chat_service.generate_study_plan(topic, document_ids)
        return {"study_plan": plan}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/explain-concept")
async def explain_concept(concept: str, document_ids: Optional[List[str]] = None):
    """Giải thích khái niệm"""
    try:
        explanation = await chat_service.explain_concept(concept, document_ids)
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
