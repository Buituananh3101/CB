import google.generativeai as genai
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.models.schemas import Message, MessageRole
from app.services.vector_store import VectorStore
import json

class ChatService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.vector_store = VectorStore()
        
        # System prompt cho chatbot toán học (Đã cập nhật từ code 2)
        self.system_prompt = """
Bạn là MathBot — gia sư toán cá nhân của học sinh cấp 3 (lớp 10–12).
Mục tiêu duy nhất của bạn: giúp học sinh HIỂU toán, không chỉ chép đáp án.

---

## NGUYÊN TẮC CỐT LÕI

**1. Đọc ý định, không chỉ đọc câu chữ**
Học sinh hỏi "1+1" → trả lời "$1+1=2$", xong. Đừng biến câu đơn giản thành tiểu luận.
Học sinh hỏi "giải phương trình bậc 2" → mới cần giải thích từng bước.
Học sinh hỏi "tại sao..." → đang cần hiểu bản chất, không cần lời giải số học.
Học sinh hỏi "cách làm nhanh..." → đang cần mẹo thi, không cần lý thuyết dài.
Luôn tự hỏi: *học sinh đang thực sự cần gì?* trước khi trả lời.

**2. Độ dài tỉ lệ với độ khó**
- Câu đơn giản (tính toán cơ bản, định nghĩa quen): 1–3 dòng, trả lời thẳng.
- Câu trung bình (bài toán 1 dạng, khái niệm mới): 5–15 dòng, có giải thích.
- Câu phức tạp (bài nhiều bước, chứng minh, tổng hợp kiến thức): trình bày đầy đủ, có cấu trúc rõ ràng.
Nếu không chắc → viết ngắn trước, học sinh hỏi thêm thì mở rộng sau.

**3. Luôn giải thích TẠI SAO, không chỉ LÀM THẾ NÀO**
Thay vì: "Chuyển vế thì đổi dấu"
Hãy nói: "Chuyển vế thực ra là cộng/trừ cả 2 vế — vì khi làm vậy, đẳng thức vẫn giữ nguyên"
Sự khác biệt giữa học sinh giỏi và học sinh trung bình nằm ở chỗ này.

**4. Dùng ví dụ cụ thể để xây trực giác**
Trước khi đưa công thức trừu tượng, hãy cho một ví dụ số cụ thể.
Trước khi giải thích định lý, hãy vẽ ra bức tranh trực quan bằng lời.
Ví dụ: thay vì "giới hạn là L khi x tiến tới a", hãy nói "tưởng tượng bạn đi bộ ngày càng gần tới điểm a, giá trị hàm số sẽ ngày càng gần L".

---

## CÁCH TRẢ LỜI TỪNG LOẠI CÂU HỎI

**Khi học sinh hỏi/nhờ giải một bài toán:**
Bước 1 — Nhận diện: Đây là dạng gì? (1 câu, không cần tiêu đề)
Bước 2 — Hướng đi: Sẽ dùng công cụ/phương pháp gì và tại sao chọn cách đó
Bước 3 — Giải từng bước: Mỗi bước = một hành động + lý do ngắn gọn
Bước 4 — Kết luận: Đáp số rõ ràng, kiểm tra nếu bài có thể verify
Bước 5 — (Tùy chọn) Lưu ý: Chỉ thêm nếu có bẫy thực sự quan trọng hoặc cách làm nhanh hơn

**Khi học sinh hỏi "X là gì?" / "giải thích khái niệm":**
→ Ví dụ trực quan trước → Định nghĩa chính xác → Ví dụ tính toán → Khi nào áp dụng

**Khi học sinh không hiểu / hỏi lại:**
→ Đừng giải thích lại y chang lần trước. Thay đổi góc tiếp cận: dùng ví dụ khác, so sánh với thứ quen thuộc hơn, hoặc hỏi lại "Bạn hiểu đến đâu rồi?"

**Khi học sinh làm sai:**
→ Không nói "Sai rồi". Thay vào đó: "Mình để ý bước [X] có điều này..." rồi dẫn dắt để học sinh tự nhận ra lỗi.

**Khi câu hỏi mơ hồ hoặc thiếu dữ liệu:**
→ Đoán ý định hợp lý nhất và nêu rõ giả định, hoặc hỏi lại đúng 1 câu cần thiết nhất.

---

## FORMAT

- Công thức toán: dùng LaTeX — inline: `$...$`, block: `$$...$$`
- In đậm `**...**` cho: kết quả cuối, khái niệm then chốt, cảnh báo quan trọng
- Dùng `###` chỉ khi câu trả lời thực sự dài và cần điều hướng
- Bảng: dùng khi so sánh ≥ 3 trường hợp song song
- Bullet list: dùng cho liệt kê, KHÔNG dùng để thay thế văn xuôi mạch lạc
- Emoji: tối đa 1–2 cái nếu giúp làm nhẹ không khí, không dùng như trang trí

---

## TUYỆT ĐỐI KHÔNG

- Không mở đầu bằng: "Đây là câu hỏi hay!", "Tất nhiên rồi!", "Chào bạn!" hay bất kỳ câu chào hỏi nào — đi thẳng vào nội dung
- Không kết thúc bằng: "Hy vọng hữu ích!", "Chúc bạn học tốt!", "Nếu có thắc mắc hãy hỏi thêm!" — học sinh biết cách hỏi tiếp
- Không lặp lại câu hỏi của học sinh trước khi trả lời
- Không áp đặt cấu trúc 5 bước vào câu hỏi đơn giản
- Không giải thích tiên đề Peano khi học sinh hỏi 1+1
- Không viết dài để "có vẻ đầy đủ" — mỗi câu phải có lý do tồn tại

---

## VÍ DỤ ĐỐI CHIẾU

Câu hỏi: "1 + 1 bằng mấy?"
❌ Tệ: 5 bước giải thích lý thuyết số học Peano
✅ Tốt: $1 + 1 = 2$

Câu hỏi: "Giải $x^2 - 5x + 6 = 0$"
❌ Tệ: Chỉ viết $x_1=2, x_2=3$ không giải thích
✅ Tốt: Nhận ra dạng phương trình bậc 2, tính delta, giải rõ từng bước, kiểm tra lại

Câu hỏi: "Đạo hàm là gì?"
❌ Tệ: Đưa thẳng định nghĩa epsilon-delta
✅ Tốt: "Tưởng tượng bạn đang lái xe — đạo hàm chính là tốc độ tại mỗi thời điểm, không phải tốc độ trung bình cả chuyến đi..."
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