from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
import uuid
from datetime import datetime
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.models.schemas import (
    ChatRequest, ChatResponse, Message, MessageRole,
    DocumentUploadResponse, Conversation,
    MindMapRequest, MindMapResponse,
    NoteRequest, Note,
    QuizRequest, QuizResponse,
    QuizResultSubmit, QuizResult
)
from app.services.document_processor import DocumentProcessor
from app.services.vector_store import VectorStore
from app.services.chat_service import ChatService
from app.services.mindmap_service import MindMapService
from app.services.note_service import NoteService
from app.services.quiz_service import QuizService
from app.repositories.conversation_repo import load_conversations, save_conversations, save_single_conversation
from app.repositories.quiz_repo import load_quiz_results, save_quiz_result, delete_quiz_result
from app.core.database import engine, Base
import app.models.db_models

# Init Database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Math Chatbot API",
    description="API cho chatbot hỗ trợ học sinh cấp 3 học toán",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

document_processor = DocumentProcessor()
vector_store = VectorStore()
chat_service = ChatService()
mindmap_service = MindMapService()
note_service = NoteService()
quiz_service = QuizService()

conversations_storage = load_conversations()
documents_storage = {}

# ==================== HEALTH CHECK ====================

# @app.get("/")
# async def root():
#     return {"message": "Math Chatbot API is running", "version": "1.0.0", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {"gemini_api": "connected", "vector_store": "active", "document_storage": "active"}
    }

# ==================== DOCUMENTS ====================

@app.post("/api/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    try:
        content = await file.read()
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=400, detail="File quá lớn.")
        await file.seek(0)
        file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        doc_data = await document_processor.process_document(file_path, file.filename)
        documents_storage[doc_data["id"]] = doc_data
        chunks = document_processor.chunk_text(doc_data["content"])
        vector_store.add_document(
            doc_id=doc_data["id"],
            content=doc_data["content"],
            metadata={"filename": doc_data["filename"], "file_type": doc_data["file_type"]},
            chunks=chunks
        )
        return DocumentUploadResponse(
            document_id=doc_data["id"], filename=doc_data["filename"],
            status="success", message="Tải tài liệu thành công"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý tài liệu: {str(e)}")

@app.get("/api/documents")
async def get_documents():
    docs = [
        {"id": d["id"], "filename": d["filename"], "file_type": d["file_type"],
         "upload_date": datetime.now().isoformat()}
        for d in documents_storage.values()
    ]
    return {"documents": docs}

@app.get("/api/documents/{document_id}")
async def get_document(document_id: str):
    if document_id not in documents_storage:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu")
    doc = documents_storage[document_id]
    return {
        "id": doc["id"], "filename": doc["filename"], "file_type": doc["file_type"],
        "content": doc["content"][:500] + "..." if len(doc["content"]) > 500 else doc["content"],
        "metadata": doc.get("metadata", {})
    }

@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    if document_id not in documents_storage:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu")
    vector_store.delete_document(document_id)
    del documents_storage[document_id]
    return {"message": "Xóa tài liệu thành công"}

# ==================== CHAT ====================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        conversation_id = request.conversation_id or str(uuid.uuid4())
        if conversation_id not in conversations_storage:
            conversations_storage[conversation_id] = Conversation(
                id=conversation_id, title=request.message[:50],
                messages=[], document_ids=request.document_ids or []
            )
        conversation = conversations_storage[conversation_id]
        conversation.messages.append(Message(role=MessageRole.USER, content=request.message))
        response_data = await chat_service.chat(
            message=request.message,
            conversation_history=conversation.messages,
            document_ids=request.document_ids
        )
        conversation.messages.append(Message(role=MessageRole.ASSISTANT, content=response_data["response"]))
        conversation.updated_at = datetime.now()
        save_single_conversation(conversations_storage, conversation_id)
        return ChatResponse(
            response=response_data["response"],
            conversation_id=conversation_id,
            sources=response_data.get("sources", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi chat: {str(e)}")

@app.get("/api/conversations")
async def get_conversations():
    convs = sorted(
        [{"id": c.id, "title": c.title, "message_count": len(c.messages),
          "created_at": c.created_at.isoformat(), "updated_at": c.updated_at.isoformat()}
         for c in conversations_storage.values()],
        key=lambda x: x["updated_at"], reverse=True
    )
    return {"conversations": convs}

@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    if conversation_id not in conversations_storage:
        raise HTTPException(status_code=404, detail="Không tìm thấy hội thoại")
    conv = conversations_storage[conversation_id]
    return {
        "id": conv.id, "title": conv.title,
        "messages": [{"role": m.role.value, "content": m.content, "timestamp": m.timestamp.isoformat()} for m in conv.messages],
        "document_ids": conv.document_ids,
        "created_at": conv.created_at.isoformat(), "updated_at": conv.updated_at.isoformat()
    }

@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    if conversation_id not in conversations_storage:
        raise HTTPException(status_code=404, detail="Không tìm thấy hội thoại")
    del conversations_storage[conversation_id]
    save_conversations(conversations_storage)
    return {"message": "Xóa hội thoại thành công"}

class RenameRequest(BaseModel):
    title: str

@app.put("/api/conversations/{conversation_id}/rename")
async def rename_conversation(conversation_id: str, body: RenameRequest):
    if conversation_id not in conversations_storage:
        raise HTTPException(status_code=404, detail="Không tìm thấy hội thoại")
    conversations_storage[conversation_id].title = body.title.strip()
    conversations_storage[conversation_id].updated_at = datetime.now()
    save_conversations(conversations_storage)
    return {"message": "Đổi tên thành công", "title": body.title.strip()}

# ==================== MINDMAP ====================

@app.post("/api/mindmap", response_model=MindMapResponse)
async def create_mindmap(request: MindMapRequest):
    try:
        root_node = await mindmap_service.generate_mindmap(
            topic=request.topic, document_ids=request.document_ids, depth=request.depth
        )
        return MindMapResponse(root_node=root_node, topic=request.topic)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tạo mindmap: {str(e)}")

@app.post("/api/concept-map")
async def create_concept_map(concepts: List[str], document_ids: Optional[List[str]] = None):
    try:
        return await mindmap_service.generate_concept_map(concepts=concepts, document_ids=document_ids)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== NOTES ====================

@app.post("/api/notes", response_model=Note)
async def create_note(request: NoteRequest):
    try:
        return await note_service.create_note(
            title=request.title, content=request.content,
            document_ids=request.document_ids, auto_generate=request.auto_generate
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/notes")
async def get_notes():
    return {"notes": note_service.get_all_notes()}

@app.get("/api/notes/{note_id}", response_model=Note)
async def get_note(note_id: str):
    note = note_service.get_note(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Không tìm thấy ghi chú")
    return note

@app.put("/api/notes/{note_id}", response_model=Note)
async def update_note(note_id: str, title: Optional[str] = None, content: Optional[str] = None):
    note = await note_service.update_note(note_id, title, content)
    if not note:
        raise HTTPException(status_code=404, detail="Không tìm thấy ghi chú")
    return note

@app.delete("/api/notes/{note_id}")
async def delete_note(note_id: str):
    if not note_service.delete_note(note_id):
        raise HTTPException(status_code=404, detail="Không tìm thấy ghi chú")
    return {"message": "Xóa ghi chú thành công"}

@app.post("/api/notes/summarize")
async def summarize_notes(note_ids: List[str]):
    return {"summary": await note_service.summarize_notes(note_ids)}

@app.get("/api/notes/{note_id}/flashcards")
async def get_flashcards(note_id: str):
    return {"flashcards": await note_service.generate_flashcards(note_id)}

# ==================== QUIZ ====================

@app.post("/api/quiz", response_model=QuizResponse)
async def create_quiz(request: QuizRequest):
    """Tạo bộ câu hỏi, trả về quiz_id để dùng khi nộp bài"""
    try:
        questions = await quiz_service.generate_quiz(
            topic=request.topic,
            num_questions=request.num_questions,
            difficulty=request.difficulty,
            document_ids=request.document_ids
        )
        return QuizResponse(
            quiz_id=str(uuid.uuid4()),
            questions=questions,
            topic=request.topic,
            difficulty=request.difficulty
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tạo quiz: {str(e)}")


@app.post("/api/quiz/submit", response_model=QuizResult)
async def submit_quiz(payload: QuizResultSubmit):
    """Nhận kết quả làm bài, tính điểm và lưu JSON"""
    try:
        correct_count = sum(1 for a in payload.answers if a.is_correct)
        total = len(payload.answers)
        score = round((correct_count / total * 100) if total > 0 else 0, 1)

        result = QuizResult(
            id=str(uuid.uuid4()),
            quiz_id=payload.quiz_id,
            topic=payload.topic,
            difficulty=payload.difficulty,
            total_questions=total,
            correct_count=correct_count,
            score=score,
            answers=payload.answers,
            completed_at=datetime.now()
        )
        save_quiz_result(result.model_dump(mode="json"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lưu kết quả: {str(e)}")


@app.get("/api/quiz/history")
async def get_quiz_history():
    """Lấy toàn bộ lịch sử làm quiz (bản tóm tắt)"""
    results = load_quiz_results()
    summaries = [
        {
            "id": r.get("id"),
            "topic": r.get("topic"),
            "difficulty": r.get("difficulty"),
            "total_questions": r.get("total_questions"),
            "correct_count": r.get("correct_count"),
            "score": r.get("score"),
            "completed_at": r.get("completed_at"),
        }
        for r in results
    ]
    return {"history": summaries}


@app.get("/api/quiz/history/{result_id}")
async def get_quiz_result_detail(result_id: str):
    """Xem chi tiết một lần làm bài"""
    results = load_quiz_results()
    for r in results:
        if r.get("id") == result_id:
            return r
    raise HTTPException(status_code=404, detail="Không tìm thấy kết quả")


@app.delete("/api/quiz/history/{result_id}")
async def delete_quiz_history_item(result_id: str):
    """Xóa một bản ghi lịch sử"""
    if not delete_quiz_result(result_id):
        raise HTTPException(status_code=404, detail="Không tìm thấy kết quả")
    return {"message": "Đã xóa"}


@app.post("/api/practice-problems")
async def create_practice_problems(
    topic: str, num_problems: int = 5,
    difficulty: str = "medium", document_ids: Optional[List[str]] = None
):
    try:
        problems = await quiz_service.generate_practice_problems(
            topic=topic, num_problems=num_problems,
            difficulty=difficulty, document_ids=document_ids
        )
        return {"problems": problems}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/check-answer")
async def check_answer(question: str, user_answer: str, correct_answer: str):
    try:
        return await quiz_service.check_answer(question, user_answer, correct_answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== UTILITY ====================

@app.post("/api/study-plan")
async def create_study_plan(topic: str, document_ids: Optional[List[str]] = None):
    try:
        return {"study_plan": await chat_service.generate_study_plan(topic, document_ids)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/explain-concept")
async def explain_concept(concept: str, document_ids: Optional[List[str]] = None):
    try:
        return {"explanation": await chat_service.explain_concept(concept, document_ids)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Phục vụ giao diện web từ thư mục static
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
