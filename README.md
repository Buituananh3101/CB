# Math Chatbot API - Backend cho Chatbot Hỗ Trợ Học Toán

## 📚 Giới thiệu

Backend FastAPI cho chatbot hỗ trợ học sinh cấp 3 học toán, được xây dựng với Gemini AI. Hệ thống có các tính năng tương tự NotebookLM:

- 💬 Chat AI thông minh dựa trên tài liệu
- 📄 Upload và xử lý tài liệu (PDF, DOCX, TXT, hình ảnh)
- 🧠 Tạo Mind Map tự động
- 📝 Tạo ghi chú thông minh
- ✅ Tạo quiz và bài tập
- 🔍 Tìm kiếm semantic với vector database

## 🚀 Cài đặt

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Cấu hình API Key

Tạo file `.env` từ `.env.example`:

```bash
cp .env.example .env
```

Sửa file `.env` và thêm API key của bạn:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
SECRET_KEY=generate_with_openssl_rand_hex_32
```

**Lấy Gemini API Key miễn phí:**
1. Truy cập: https://makersuite.google.com/app/apikey
2. Đăng nhập bằng Google Account
3. Tạo API key mới
4. Copy và paste vào file `.env`

### 3. Chạy server

```bash
python main.py
```

Hoặc với uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server sẽ chạy tại: `http://localhost:8000`

## 📖 API Documentation

Sau khi chạy server, truy cập:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔌 API Endpoints

### 📄 Document Management

#### Upload tài liệu
```http
POST /api/documents/upload
Content-Type: multipart/form-data

file: [file PDF/DOCX/TXT/Image]
```

**Response:**
```json
{
  "document_id": "uuid-string",
  "filename": "bai_giang_toan.pdf",
  "status": "success",
  "message": "Tải tài liệu thành công"
}
```

#### Lấy danh sách tài liệu
```http
GET /api/documents
```

#### Xem chi tiết tài liệu
```http
GET /api/documents/{document_id}
```

#### Xóa tài liệu
```http
DELETE /api/documents/{document_id}
```

### 💬 Chat

#### Chat với AI
```http
POST /api/chat
Content-Type: application/json

{
  "message": "Giải thích định lý Pythagoras",
  "conversation_id": "optional-uuid",
  "document_ids": ["doc-id-1", "doc-id-2"]
}
```

**Response:**
```json
{
  "response": "Định lý Pythagoras phát biểu rằng...",
  "conversation_id": "uuid",
  "sources": [
    {
      "content": "Nội dung từ tài liệu...",
      "metadata": {...}
    }
  ],
  "timestamp": "2024-01-01T00:00:00"
}
```

#### Lấy danh sách hội thoại
```http
GET /api/conversations
```

#### Xem chi tiết hội thoại
```http
GET /api/conversations/{conversation_id}
```

### 🧠 Mind Map

#### Tạo Mind Map
```http
POST /api/mindmap
Content-Type: application/json

{
  "topic": "Hàm số bậc hai",
  "document_ids": ["doc-id-1"],
  "depth": 3
}
```

**Response:**
```json
{
  "root_node": {
    "id": "uuid",
    "text": "Hàm số bậc hai",
    "children": [
      {
        "id": "uuid",
        "text": "Định nghĩa",
        "children": [...],
        "level": 1,
        "color": "#4ECDC4"
      }
    ],
    "level": 0,
    "color": "#FF6B6B"
  },
  "topic": "Hàm số bậc hai"
}
```

#### Tạo Concept Map
```http
POST /api/concept-map
Content-Type: application/json

{
  "concepts": ["Đạo hàm", "Tích phân", "Giới hạn"],
  "document_ids": ["doc-id-1"]
}
```

### 📝 Notes (Ghi chú)

#### Tạo ghi chú mới
```http
POST /api/notes
Content-Type: application/json

{
  "title": "Tổng hợp kiến thức về Đạo hàm",
  "content": "Nội dung tùy chọn",
  "document_ids": ["doc-id-1", "doc-id-2"],
  "auto_generate": true
}
```

#### Lấy tất cả ghi chú
```http
GET /api/notes
```

#### Xem chi tiết ghi chú
```http
GET /api/notes/{note_id}
```

#### Cập nhật ghi chú
```http
PUT /api/notes/{note_id}
Content-Type: application/json

{
  "title": "Tiêu đề mới",
  "content": "Nội dung mới"
}
```

#### Tạo flashcards từ ghi chú
```http
GET /api/notes/{note_id}/flashcards
```

**Response:**
```json
{
  "flashcards": [
    {
      "front": "Đạo hàm của hàm số y = x² là gì?",
      "back": "y' = 2x"
    }
  ]
}
```

### ✅ Quiz & Practice

#### Tạo bài quiz trắc nghiệm
```http
POST /api/quiz
Content-Type: application/json

{
  "topic": "Phương trình bậc hai",
  "num_questions": 5,
  "difficulty": "medium",
  "document_ids": ["doc-id-1"]
}
```

**Response:**
```json
{
  "questions": [
    {
      "question": "Phương trình x² - 5x + 6 = 0 có nghiệm là?",
      "options": ["A. x = 2, x = 3", "B. x = 1, x = 6", "C. x = -2, x = -3", "D. Vô nghiệm"],
      "correct_answer": 0,
      "explanation": "Giải chi tiết...",
      "difficulty": "medium"
    }
  ],
  "topic": "Phương trình bậc hai"
}
```

#### Tạo bài tập tự luận
```http
POST /api/practice-problems?topic=Đạo+hàm&num_problems=5&difficulty=medium
```

#### Kiểm tra câu trả lời
```http
POST /api/check-answer
Content-Type: application/json

{
  "question": "Tính đạo hàm của y = x²",
  "user_answer": "y' = 2x",
  "correct_answer": "y' = 2x"
}
```

### 🎯 Utility

#### Tạo kế hoạch học tập
```http
POST /api/study-plan?topic=Giải+tích+12
```

#### Giải thích khái niệm
```http
POST /api/explain-concept
Content-Type: application/json

{
  "concept": "Đạo hàm",
  "document_ids": ["doc-id-1"]
}
```

## 🔧 Cấu trúc Project

```
├── main.py                 # FastAPI application chính
├── config.py              # Cấu hình
├── models.py              # Pydantic models
├── document_processor.py  # Xử lý tài liệu
├── vector_store.py        # Vector database (ChromaDB)
├── chat_service.py        # Chat với Gemini
├── mindmap_service.py     # Tạo mind map
├── note_service.py        # Quản lý ghi chú
├── quiz_service.py        # Tạo quiz
├── requirements.txt       # Dependencies
├── .env.example          # Template cấu hình
└── README.md             # Hướng dẫn
```

## 💡 Ví dụ Frontend Integration

### Sử dụng với fetch API (JavaScript)

```javascript
// Upload tài liệu
async function uploadDocument(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://localhost:8000/api/documents/upload', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
}

// Chat
async function sendMessage(message, documentIds = []) {
  const response = await fetch('http://localhost:8000/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message: message,
      document_ids: documentIds
    })
  });
  
  return await response.json();
}

// Tạo mind map
async function createMindMap(topic, documentIds = []) {
  const response = await fetch('http://localhost:8000/api/mindmap', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      topic: topic,
      document_ids: documentIds,
      depth: 3
    })
  });
  
  return await response.json();
}
```

### HTML Form Example

```html
<!DOCTYPE html>
<html>
<head>
    <title>Math Chatbot</title>
</head>
<body>
    <h1>Math Chatbot</h1>
    
    <!-- Upload Form -->
    <form id="uploadForm">
        <input type="file" id="fileInput" accept=".pdf,.docx,.txt,.jpg,.png">
        <button type="submit">Upload</button>
    </form>
    
    <!-- Chat -->
    <div id="chat">
        <div id="messages"></div>
        <input type="text" id="messageInput" placeholder="Hỏi gì đó...">
        <button onclick="sendMessage()">Gửi</button>
    </div>
    
    <script>
        // Upload handler
        document.getElementById('uploadForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const file = document.getElementById('fileInput').files[0];
            
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch('http://localhost:8000/api/documents/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            alert('Upload thành công: ' + result.document_id);
        });
        
        // Chat handler
        async function sendMessage() {
            const message = document.getElementById('messageInput').value;
            
            const response = await fetch('http://localhost:8000/api/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: message})
            });
            
            const result = await response.json();
            document.getElementById('messages').innerHTML += 
                `<p><strong>Bạn:</strong> ${message}</p>
                 <p><strong>AI:</strong> ${result.response}</p>`;
            
            document.getElementById('messageInput').value = '';
        }
    </script>
</body>
</html>
```

## 🎨 Tính năng nổi bật

### 1. RAG (Retrieval-Augmented Generation)
- Upload tài liệu và chat dựa trên nội dung tài liệu
- Sử dụng ChromaDB để lưu trữ vector embeddings
- Tìm kiếm semantic thông minh

### 2. Mind Map tự động
- Tạo sơ đồ tư duy từ chủ đề
- Phân tầng logic và rõ ràng
- Export dạng JSON để render trên frontend

### 3. Ghi chú thông minh
- Tự động tạo nội dung từ tài liệu
- Tạo flashcards để ôn tập
- Tóm tắt nhiều ghi chú

### 4. Quiz & Bài tập
- Tạo câu hỏi trắc nghiệm tự động
- Tạo bài tập tự luận có lời giải
- Chấm và nhận xét bài làm

## 🔒 Bảo mật

- CORS đã được cấu hình
- Giới hạn kích thước file upload
- Validate input
- Error handling đầy đủ

## 📝 Lưu ý

1. **API Key**: Gemini API free có giới hạn request/phút. Nếu dùng production nên nâng cấp.

2. **Storage**: Hiện tại dùng in-memory storage. Với production nên dùng:
   - PostgreSQL/MySQL cho metadata
   - S3/Cloud Storage cho files
   - Redis cho cache

3. **Vector Store**: ChromaDB persistent. Dữ liệu lưu ở `./vector_store/`

4. **Scalability**: Có thể deploy lên:
   - Heroku
   - Railway
   - Google Cloud Run
   - AWS Lambda

## 🐛 Troubleshooting

### Lỗi "Module not found"
```bash
pip install -r requirements.txt
```

### Lỗi Gemini API
- Kiểm tra API key trong `.env`
- Kiểm tra quota tại https://makersuite.google.com

### Lỗi ChromaDB
```bash
rm -rf ./vector_store/
# Restart server
```

## 📞 Hỗ trợ

Nếu gặp vấn đề, hãy:
1. Kiểm tra logs
2. Xem API documentation tại `/docs`
3. Test với Postman/Thunder Client

## 🚀 Roadmap

- [ ] Authentication & Authorization
- [ ] Database persistence (PostgreSQL)
- [ ] Real-time chat với **WebSocket**
- [ ] Export notes sang PDF/DOCX
- [ ] Nhiều AI models (GPT-4, Claude)
- [ ] Mobile app support
- [ ] Collaborative features

## 📄 License

MIT License - Free to use for educational purposes
