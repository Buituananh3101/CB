import google.generativeai as genai
from typing import List, Dict, Any, Optional
from config import settings
from models import Message, MessageRole
from vector_store import VectorStore
import json

class ChatService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.vector_store = VectorStore()
        
        # System prompt cho chatbot toán học
        self.system_prompt = """
        Bạn là một trợ lý AI chuyên hỗ trợ học sinh cấp 3 học Toán.
        
        Nhiệm vụ của bạn:
        - Giải thích các khái niệm toán học một cách dễ hiểu
        - Hướng dẫn giải bài tập từng bước
        - Cung cấp ví dụ minh họa cụ thể
        - Khuyến khích tư duy logic và phương pháp giải quyết vấn đề
        - Luôn kiên nhẫn và thân thiện với học sinh
        
        Khi trả lời:
        - Sử dụng ngôn ngữ đơn giản, phù hợp với học sinh cấp 3
        - Chia nhỏ các bước giải
        - Đưa ra ví dụ cụ thể
        - Giải thích "tại sao" chứ không chỉ "như thế nào"
        - Khuyến khích học sinh tự suy nghĩ trước khi đưa ra đáp án
        
        Nếu có tài liệu tham khảo, hãy dựa vào nội dung đó để trả lời chính xác hơn.
        """
    
    async def chat(
        self, 
        message: str, 
        conversation_history: List[Message] = [],
        document_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Xử lý chat với context từ documents"""
        
        # Tìm kiếm thông tin liên quan từ documents
        relevant_docs = []
        if document_ids:
            relevant_docs = self.vector_store.search(
                query=message,
                document_ids=document_ids,
                top_k=3
            )
        
        # Xây dựng context từ documents
        context = ""
        if relevant_docs:
            context = "\n\nTHÔNG TIN TỪ TÀI LIỆU THAM KHẢO:\n"
            for i, doc in enumerate(relevant_docs, 1):
                context += f"\n[Nguồn {i}]:\n{doc['content']}\n"
        
        # Xây dựng conversation history
        history_text = ""
        for msg in conversation_history[-5:]:  # Lấy 5 tin nhắn gần nhất
            role = "Học sinh" if msg.role == MessageRole.USER else "Trợ lý"
            history_text += f"\n{role}: {msg.content}\n"
        
        # Tạo prompt đầy đủ
        full_prompt = f"""
        {self.system_prompt}
        
        {context}
        
        LỊCH SỬ HỘI THOẠI:
        {history_text}
        
        HỌC SINH HỎI: {message}
        
        TRỢ LÝ TRẢ LỜI:
        """
        
        try:
            # Gọi Gemini API
            response = self.model.generate_content(full_prompt)
            
            return {
                "response": response.text,
                "sources": [
                    {
                        "content": doc['content'][:200] + "...",
                        "metadata": doc['metadata']
                    }
                    for doc in relevant_docs
                ]
            }
        except Exception as e:
            return {
                "response": f"Xin lỗi, đã có lỗi xảy ra: {str(e)}. Vui lòng thử lại.",
                "sources": []
            }
    
    async def generate_study_plan(self, topic: str, document_ids: Optional[List[str]] = None) -> str:
        """Tạo kế hoạch học tập"""
        
        # Lấy thông tin từ documents
        context = ""
        if document_ids:
            relevant_docs = self.vector_store.search(
                query=topic,
                document_ids=document_ids,
                top_k=5
            )
            if relevant_docs:
                context = "Dựa trên tài liệu:\n"
                for doc in relevant_docs:
                    context += f"- {doc['content'][:300]}...\n"
        
        prompt = f"""
        Hãy tạo một kế hoạch học tập chi tiết cho chủ đề: {topic}
        
        {context}
        
        Kế hoạch cần bao gồm:
        1. Mục tiêu học tập
        2. Các khái niệm cần nắm
        3. Trình tự học tập hợp lý
        4. Bài tập thực hành đề xuất
        5. Thời gian ước tính
        6. Tips học tập hiệu quả
        
        Trả lời bằng tiếng Việt, phù hợp với học sinh cấp 3.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Không thể tạo kế hoạch học tập: {str(e)}"
    
    async def explain_concept(self, concept: str, document_ids: Optional[List[str]] = None) -> str:
        """Giải thích khái niệm toán học"""
        
        context = ""
        if document_ids:
            relevant_docs = self.vector_store.search(
                query=concept,
                document_ids=document_ids,
                top_k=3
            )
            if relevant_docs:
                context = "Thông tin từ tài liệu:\n"
                for doc in relevant_docs:
                    context += f"{doc['content'][:400]}\n\n"
        
        prompt = f"""
        Hãy giải thích khái niệm toán học sau cho học sinh cấp 3: {concept}
        
        {context}
        
        Yêu cầu:
        - Giải thích đơn giản, dễ hiểu
        - Đưa ra ví dụ cụ thể trong thực tế
        - Liên hệ với kiến thức đã học
        - Sử dụng hình ảnh minh họa (mô tả bằng lời nếu cần)
        - Kết thúc bằng vài câu hỏi kiểm tra hiểu biết
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Không thể giải thích khái niệm: {str(e)}"
