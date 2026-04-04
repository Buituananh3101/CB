import google.generativeai as genai
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.models.schemas import Note
from app.services.vector_store import VectorStore
import uuid
from datetime import datetime

class NoteService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.vector_store = VectorStore()
        self.notes_storage: Dict[str, Note] = {}
    
    async def create_note(
        self,
        title: str,
        content: Optional[str] = None,
        document_ids: Optional[List[str]] = None,
        auto_generate: bool = True
    ) -> Note:
        """Tạo ghi chú mới"""
        
        note_id = str(uuid.uuid4())
        
        # Nếu auto_generate và có documents, tạo nội dung tự động
        if auto_generate and document_ids:
            generated_content = await self._generate_note_content(title, document_ids)
            if not content:
                content = generated_content
            else:
                content = f"{content}\n\n--- Nội dung tự động tạo ---\n{generated_content}"
        
        if not content:
            content = ""
        
        note = Note(
            id=note_id,
            title=title,
            content=content,
            document_ids=document_ids or [],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags=self._extract_tags(content)
        )
        
        self.notes_storage[note_id] = note
        return note
    
    async def _generate_note_content(self, title: str, document_ids: List[str]) -> str:
        """Tạo nội dung ghi chú tự động từ documents"""
        
        # Lấy thông tin từ documents
        relevant_docs = self.vector_store.search(
            query=title,
            document_ids=document_ids,
            top_k=5
        )
        
        context = ""
        if relevant_docs:
            context = "Thông tin từ tài liệu:\n\n"
            for i, doc in enumerate(relevant_docs, 1):
                context += f"[{i}] {doc['content'][:600]}\n\n"
        
        prompt = f"""
        Tạo một bài ghi chú học tập chi tiết về chủ đề: {title}
        
        {context}
        
        Ghi chú cần bao gồm:
        1. TỔNG QUAN
           - Định nghĩa và khái niệm cơ bản
           - Tầm quan trọng của chủ đề
        
        2. NỘI DUNG CHI TIẾT
           - Các định lý, công thức chính
           - Cách áp dụng và ví dụ minh họa
           - Các lưu ý khi giải bài
        
        3. VÍ DỤ MINH HỌA
           - Ít nhất 2 ví dụ có lời giải chi tiết
        
        4. BÀI TẬP ÔN LUYỆN
           - 3-5 bài tập tự luyện (có gợi ý)
        
        5. GHI NHỚ NHANH
           - Tips và tricks
           - Cách nhớ công thức
        
        Viết bằng tiếng Việt, rõ ràng, dễ hiểu cho học sinh cấp 3.
        Sử dụng formatting markdown: ## cho tiêu đề, ** cho in đậm, ``` cho công thức.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Không thể tạo nội dung ghi chú: {str(e)}"
    
    def _extract_tags(self, content: str) -> List[str]:
        """Trích xuất tags từ nội dung"""
        # Danh sách các tags phổ biến trong toán học
        common_tags = [
            "đại số", "hình học", "giải tích", "lượng giác", "số học",
            "phương trình", "bất phương trình", "hàm số", "đạo hàm",
            "tích phân", "véc tơ", "tọa độ", "xác suất", "thống kê",
            "dãy số", "cấp số", "logarit", "mũ", "định lý"
        ]
        
        tags = []
        content_lower = content.lower()
        
        for tag in common_tags:
            if tag in content_lower:
                tags.append(tag)
        
        return tags[:5]  # Giới hạn 5 tags
    
    def get_note(self, note_id: str) -> Optional[Note]:
        """Lấy ghi chú theo ID"""
        return self.notes_storage.get(note_id)
    
    def get_all_notes(self) -> List[Note]:
        """Lấy tất cả ghi chú"""
        return list(self.notes_storage.values())
    
    async def update_note(self, note_id: str, title: Optional[str] = None, content: Optional[str] = None) -> Optional[Note]:
        """Cập nhật ghi chú"""
        note = self.notes_storage.get(note_id)
        if not note:
            return None
        
        if title:
            note.title = title
        if content:
            note.content = content
            note.tags = self._extract_tags(content)
        
        note.updated_at = datetime.now()
        return note
    
    def delete_note(self, note_id: str) -> bool:
        """Xóa ghi chú"""
        if note_id in self.notes_storage:
            del self.notes_storage[note_id]
            return True
        return False
    
    async def summarize_notes(self, note_ids: List[str]) -> str:
        """Tóm tắt nhiều ghi chú"""
        notes = [self.notes_storage[nid] for nid in note_ids if nid in self.notes_storage]
        
        if not notes:
            return "Không tìm thấy ghi chú nào."
        
        combined_content = "\n\n".join([
            f"### {note.title}\n{note.content[:500]}..."
            for note in notes
        ])
        
        prompt = f"""
        Hãy tóm tắt và tổng hợp kiến thức từ các ghi chú sau:
        
        {combined_content}
        
        Tóm tắt cần:
        - Xác định các chủ đề chính
        - Liên kết các khái niệm liên quan
        - Đưa ra những điểm quan trọng nhất
        - Gợi ý cách ôn tập hiệu quả
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Không thể tóm tắt: {str(e)}"
    
    async def generate_flashcards(self, note_id: str) -> List[Dict[str, str]]:
        """Tạo flashcards từ ghi chú"""
        note = self.notes_storage.get(note_id)
        if not note:
            return []
        
        prompt = f"""
        Từ nội dung ghi chú sau, tạo 10 flashcards (thẻ ghi nhớ) để ôn tập:
        
        {note.content[:2000]}
        
        Mỗi flashcard có:
        - Mặt trước: Câu hỏi hoặc khái niệm
        - Mặt sau: Câu trả lời hoặc giải thích
        
        Trả về JSON array:
        [
            {{"front": "Câu hỏi 1?", "back": "Trả lời 1"}},
            {{"front": "Câu hỏi 2?", "back": "Trả lời 2"}}
        ]
        
        CHỈ TRẢ VỀ JSON.
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            import json
            flashcards = json.loads(response_text)
            return flashcards
        except Exception as e:
            return [{"front": "Lỗi tạo flashcard", "back": str(e)}]
