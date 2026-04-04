import google.generativeai as genai
from typing import List, Optional
from app.core.config import settings
from app.models.schemas import QuizQuestion
from app.services.vector_store import VectorStore
import json

class QuizService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.vector_store = VectorStore()
    
    async def generate_quiz(
        self,
        topic: str,
        num_questions: int = 5,
        difficulty: str = "medium",
        document_ids: Optional[List[str]] = None
    ) -> List[QuizQuestion]:
        """Tạo bài quiz/kiểm tra"""
        
        # Lấy context từ documents
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
                    context += f"{doc['content'][:400]}\n\n"
        
        difficulty_map = {
            "easy": "dễ (dành cho học sinh trung bình)",
            "medium": "trung bình (yêu cầu hiểu và vận dụng)",
            "hard": "khó (yêu cầu tư duy cao)"
        }
        
        prompt = f"""
        Tạo {num_questions} câu hỏi trắc nghiệm về chủ đề: {topic}
        
        {context}
        
        Độ khó: {difficulty_map.get(difficulty, "medium")}
        
        Yêu cầu:
        - Mỗi câu hỏi có 4 đáp án A, B, C, D
        - Chỉ có 1 đáp án đúng
        - Câu hỏi phải rõ ràng, chính xác
        - Đáp án sai phải hợp lý (không quá dễ loại trừ)
        - Có giải thích chi tiết cho đáp án đúng
        
        Trả về JSON array:
        [
            {{
                "question": "Câu hỏi...",
                "options": ["A. Đáp án 1", "B. Đáp án 2", "C. Đáp án 3", "D. Đáp án 4"],
                "correct_answer": 0,
                "explanation": "Giải thích chi tiết...",
                "difficulty": "easy"
            }}
        ]
        
        correct_answer là index của đáp án đúng (0, 1, 2, hoặc 3).
        CHỈ TRẢ VỀ JSON, KHÔNG CÓ TEXT KHÁC.
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Làm sạch response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            questions_data = json.loads(response_text)
            
            # Convert to QuizQuestion objects
            questions = []
            for q_data in questions_data:
                question = QuizQuestion(
                    question=q_data["question"],
                    options=q_data["options"],
                    correct_answer=q_data["correct_answer"],
                    explanation=q_data["explanation"],
                    difficulty=q_data.get("difficulty", difficulty)
                )
                questions.append(question)
            
            return questions
            
        except Exception as e:
            print(f"Lỗi tạo quiz: {str(e)}")
            # Fallback: tạo câu hỏi mẫu
            return [
                QuizQuestion(
                    question=f"Câu hỏi về {topic}?",
                    options=["A. Đáp án 1", "B. Đáp án 2", "C. Đáp án 3", "D. Đáp án 4"],
                    correct_answer=0,
                    explanation="Vui lòng thử lại để tạo câu hỏi chi tiết hơn.",
                    difficulty=difficulty
                )
            ]
    
    async def generate_practice_problems(
        self,
        topic: str,
        num_problems: int = 5,
        difficulty: str = "medium",
        document_ids: Optional[List[str]] = None
    ) -> List[dict]:
        """Tạo bài tập tự luận"""
        
        context = ""
        if document_ids:
            relevant_docs = self.vector_store.search(
                query=topic,
                document_ids=document_ids,
                top_k=3
            )
            if relevant_docs:
                context = "Tham khảo:\n"
                for doc in relevant_docs:
                    context += f"{doc['content'][:300]}\n"
        
        difficulty_desc = {
            "easy": "cơ bản, áp dụng trực tiếp công thức",
            "medium": "vận dụng, kết hợp nhiều kiến thức",
            "hard": "nâng cao, yêu cầu tư duy sáng tạo"
        }
        
        prompt = f"""
        Tạo {num_problems} bài tập tự luận về: {topic}
        
        {context}
        
        Độ khó: {difficulty_desc.get(difficulty, "medium")}
        
        Mỗi bài tập cần có:
        - Đề bài rõ ràng
        - Hướng dẫn giải chi tiết từng bước
        - Đáp số cuối cùng
        - Gợi ý nếu làm sai
        
        Trả về JSON:
        [
            {{
                "problem": "Đề bài...",
                "solution": "Lời giải chi tiết...",
                "answer": "Đáp số",
                "hints": ["Gợi ý 1", "Gợi ý 2"],
                "difficulty": "medium"
            }}
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
            
            problems = json.loads(response_text)
            return problems
            
        except Exception as e:
            return [{
                "problem": f"Bài tập về {topic}",
                "solution": "Lời giải đang được tạo...",
                "answer": "",
                "hints": ["Thử lại để có bài tập chi tiết"],
                "difficulty": difficulty
            }]
    
    async def check_answer(self, question: str, user_answer: str, correct_answer: str) -> dict:
        """Kiểm tra và chấm điểm câu trả lời"""
        
        prompt = f"""
        Kiểm tra câu trả lời của học sinh:
        
        Câu hỏi: {question}
        Đáp án đúng: {correct_answer}
        Câu trả lời của học sinh: {user_answer}
        
        Hãy:
        1. So sánh và đánh giá câu trả lời
        2. Chỉ ra điểm đúng và điểm sai
        3. Giải thích tại sao đáp án đúng là như vậy
        4. Cho điểm (0-10)
        5. Đưa ra lời khuyên cải thiện
        
        Trả về JSON:
        {{
            "is_correct": true/false,
            "score": 8.5,
            "feedback": "Nhận xét chi tiết...",
            "improvements": ["Lời khuyên 1", "Lời khuyên 2"]
        }}
        
        CHỈ TRẢ VỀ JSON.
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            return json.loads(response_text)
            
        except Exception as e:
            return {
                "is_correct": False,
                "score": 0,
                "feedback": f"Không thể chấm bài: {str(e)}",
                "improvements": ["Vui lòng thử lại"]
            }
