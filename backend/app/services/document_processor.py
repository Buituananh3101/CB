import os
import uuid
from typing import List, Dict, Any, Optional
from PyPDF2 import PdfReader
from docx import Document as DocxDocument
from PIL import Image
import base64
from io import BytesIO
import google.generativeai as genai
from app.core.config import settings

class DocumentProcessor:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.vision_model = genai.GenerativeModel('gemini-2.5-flash')
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Trích xuất text từ file PDF"""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Lỗi khi đọc PDF: {str(e)}")
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Trích xuất text từ file DOCX"""
        try:
            doc = DocxDocument(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise Exception(f"Lỗi khi đọc DOCX: {str(e)}")
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Trích xuất text từ file TXT"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            raise Exception(f"Lỗi khi đọc TXT: {str(e)}")
    
    async def extract_text_from_image(self, file_path: str) -> str:
        """Trích xuất text từ hình ảnh bằng Gemini Vision"""
        try:
            image = Image.open(file_path)
            
            # Sử dụng Gemini Vision để OCR
            prompt = """
            Đây là một tài liệu học toán. Hãy trích xuất toàn bộ nội dung văn bản và công thức toán học từ hình ảnh này.
            Với công thức toán học, hãy viết chúng ở dạng LaTeX hoặc text dễ đọc.
            Giữ nguyên cấu trúc và định dạng của tài liệu.
            """
            
            response = self.vision_model.generate_content([prompt, image])
            return response.text
        except Exception as e:
            raise Exception(f"Lỗi khi đọc hình ảnh: {str(e)}")
    
    async def process_document(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Xử lý tài liệu và trả về nội dung"""
        file_extension = filename.lower().split('.')[-1]
        
        try:
            if file_extension == 'pdf':
                content = self.extract_text_from_pdf(file_path)
                doc_type = "pdf"
            elif file_extension in ['docx', 'doc']:
                content = self.extract_text_from_docx(file_path)
                doc_type = "docx"
            elif file_extension == 'txt':
                content = self.extract_text_from_txt(file_path)
                doc_type = "txt"
            elif file_extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
                content = await self.extract_text_from_image(file_path)
                doc_type = "image"
            else:
                raise Exception(f"Định dạng file không được hỗ trợ: {file_extension}")
            
            # Tạo document ID
            doc_id = str(uuid.uuid4())
            
            return {
                "id": doc_id,
                "filename": filename,
                "file_type": doc_type,
                "content": content,
                "metadata": {
                    "file_size": os.path.getsize(file_path),
                    "extension": file_extension
                }
            }
        except Exception as e:
            raise Exception(f"Lỗi xử lý tài liệu: {str(e)}")
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Chia nhỏ text thành các chunks để embedding"""
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        
        return chunks
    
    def summarize_document(self, content: str) -> str:
        """Tóm tắt nội dung tài liệu"""
        try:
            prompt = f"""
            Hãy tóm tắt nội dung tài liệu học toán sau đây một cách ngắn gọn và súc tích.
            Tập trung vào các khái niệm chính, công thức quan trọng và ví dụ.
            
            Nội dung:
            {content[:3000]}  # Giới hạn để tránh vượt quá token limit
            """
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Không thể tóm tắt: {str(e)}"
