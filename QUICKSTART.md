# 🚀 HƯỚNG DẪN KHỞI ĐỘNG NHANH

## Bước 1: Cài đặt Python

Cần Python 3.9 trở lên. Kiểm tra version:
```bash
python --version
```

Nếu chưa có, tải tại: https://www.python.org/downloads/

## Bước 2: Clone/Download Project

Download tất cả files về một thư mục, ví dụ: `math-chatbot-backend`

## Bước 3: Cài đặt Dependencies

Mở terminal/cmd tại thư mục project:

```bash
pip install -r requirements.txt
```

**Lưu ý:** Nếu gặp lỗi, thử:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Bước 4: Lấy Gemini API Key (MIỄN PHÍ)

1. Truy cập: https://makersuite.google.com/app/apikey
2. Đăng nhập bằng Google Account
3. Click "Create API Key" → chọn project (hoặc tạo mới)
4. Copy API key (dạng: `AIzaSy...`)

## Bước 5: Cấu hình API Key

Tạo file `.env` trong thư mục project:

```bash
# Windows
copy .env.example .env

# Mac/Linux
cp .env.example .env
```

Mở file `.env` và điền API key:

```env
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXX  # Thay bằng API key thật
SECRET_KEY=my-secret-key-12345
```

**Tạo SECRET_KEY ngẫu nhiên:**
```bash
# Python
python -c "import secrets; print(secrets.token_hex(32))"

# Hoặc dùng bất kỳ string nào
```

## Bước 6: Chạy Server

```bash
python main.py
```

Hoặc:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server sẽ chạy tại: `http://localhost:8000`

## Bước 7: Test API

### Option 1: Mở Browser
```
http://localhost:8000/docs
```

### Option 2: Test bằng Script
```bash
python test_api.py
```

### Option 3: Demo Frontend
Mở file `demo.html` bằng browser (Chrome, Firefox, Edge...)

## ✅ Kiểm tra xem đã chạy thành công

1. Mở browser: `http://localhost:8000/health`
2. Nếu thấy: `{"status":"healthy",...}` → Thành công! ✅

## 📝 Các lệnh hữu ích

```bash
# Chạy server với auto-reload (development)
uvicorn main:app --reload

# Chỉ định port khác
uvicorn main:app --port 5000

# Chạy test tự động
python test_api.py --auto

# Xem logs chi tiết
python main.py
```

## 🐛 Xử lý lỗi thường gặp

### Lỗi: "Module not found"
```bash
pip install -r requirements.txt
```

### Lỗi: "Invalid API key"
- Kiểm tra lại GEMINI_API_KEY trong file `.env`
- Đảm bảo không có khoảng trắng thừa
- API key phải bắt đầu bằng `AIza`

### Lỗi: "Port 8000 already in use"
```bash
# Chạy trên port khác
uvicorn main:app --port 5000
```

### Lỗi khi upload file
- Kiểm tra thư mục `uploads/` đã được tạo
- Đảm bảo file < 10MB
- Format hỗ trợ: PDF, DOCX, TXT, JPG, PNG

### ChromaDB error
```bash
# Xóa database và tạo lại
rm -rf vector_store/
# Chạy lại server
python main.py
```

## 💡 Tips sử dụng

### 1. Upload tài liệu trước khi chat
- Upload các file PDF/DOCX về toán
- Chat sẽ dựa vào nội dung tài liệu để trả lời chính xác hơn

### 2. Sử dụng document_ids
Khi chat, truyền `document_ids` để AI tham khảo tài liệu cụ thể:

```javascript
{
  "message": "Giải thích về đạo hàm",
  "document_ids": ["abc-123", "def-456"]
}
```

### 3. Tạo ghi chú tự động
Sau khi upload tài liệu, tạo ghi chú tự động:
```javascript
POST /api/notes
{
  "title": "Tổng hợp Đạo hàm",
  "document_ids": ["abc-123"],
  "auto_generate": true
}
```

### 4. Quiz từ tài liệu
Tạo quiz dựa trên tài liệu đã upload:
```javascript
POST /api/quiz
{
  "topic": "Hàm số",
  "num_questions": 5,
  "document_ids": ["abc-123"]
}
```

## 🎯 Flow sử dụng đề xuất

1. **Upload tài liệu** → `/api/documents/upload`
2. **Xem danh sách** → `/api/documents`
3. **Chat với tài liệu** → `/api/chat` (với document_ids)
4. **Tạo mind map** → `/api/mindmap`
5. **Tạo ghi chú** → `/api/notes`
6. **Tạo quiz** → `/api/quiz`

## 🔗 Links quan trọng

- API Documentation: http://localhost:8000/docs
- Demo Frontend: Mở file `demo.html`
- Health Check: http://localhost:8000/health
- Gemini API: https://makersuite.google.com

## 📞 Cần trợ giúp?

### Kiểm tra logs
```bash
# Xem logs khi chạy server
python main.py
```

### Test từng endpoint
```bash
# Interactive testing
python test_api.py
```

### Xem API Documentation
```
http://localhost:8000/docs
```

## 🎉 Chúc bạn thành công!

Bây giờ bạn đã có một backend chatbot toán học hoàn chỉnh với:
- ✅ Chat AI thông minh
- ✅ Upload và xử lý tài liệu
- ✅ RAG (Retrieval-Augmented Generation)
- ✅ Mind Map tự động
- ✅ Ghi chú thông minh
- ✅ Quiz và bài tập

Frontend của bạn chỉ cần gọi các API này!

---

**Next Steps:**
1. Tích hợp với frontend React/Vue/Angular
2. Deploy lên cloud (Heroku, Railway, Google Cloud)
3. Thêm authentication
4. Thêm database thật (PostgreSQL)
5. Cải thiện UI/UX
