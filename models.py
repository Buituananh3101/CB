from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    IMAGE = "image"

class Message(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    document_ids: Optional[List[str]] = []

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    sources: Optional[List[Dict[str, Any]]] = []
    timestamp: datetime = Field(default_factory=datetime.now)

class Document(BaseModel):
    id: str
    filename: str
    file_type: DocumentType
    upload_date: datetime = Field(default_factory=datetime.now)
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    message: str

class Conversation(BaseModel):
    id: str
    title: str
    messages: List[Message] = []
    document_ids: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class MindMapNode(BaseModel):
    id: str
    text: str
    children: List['MindMapNode'] = []
    level: int = 0
    color: Optional[str] = None

class MindMapRequest(BaseModel):
    topic: str
    document_ids: Optional[List[str]] = []
    depth: int = 3

class MindMapResponse(BaseModel):
    root_node: MindMapNode
    topic: str

class NoteRequest(BaseModel):
    title: str
    content: Optional[str] = None
    document_ids: Optional[List[str]] = []
    auto_generate: bool = True

class Note(BaseModel):
    id: str
    title: str
    content: str
    document_ids: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = []

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: int
    explanation: str
    difficulty: str  # easy, medium, hard

class QuizRequest(BaseModel):
    topic: str
    num_questions: int = 5
    difficulty: str = "medium"
    document_ids: Optional[List[str]] = []

class QuizResponse(BaseModel):
    questions: List[QuizQuestion]
    topic: str
