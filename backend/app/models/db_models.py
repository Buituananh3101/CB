from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
import datetime
from app.core.database import Base
import json

class DBConversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    document_ids = Column(String, default="[]") # Lưu dạng JSON array
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    messages = relationship("DBMessage", back_populates="conversation", cascade="all, delete-orphan")

class DBMessage(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(String, ForeignKey("conversations.id", ondelete="CASCADE"))
    role = Column(String) # 'user', 'assistant', 'system'
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.now)

    conversation = relationship("DBConversation", back_populates="messages")

class DBDocument(Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True, index=True)
    filename = Column(String)
    file_type = Column(String)
    content = Column(Text)
    metadata_json = Column(Text, default="{}")
    upload_date = Column(DateTime, default=datetime.datetime.now)

class DBQuizResult(Base):
    __tablename__ = "quiz_results"

    id = Column(String, primary_key=True, index=True)
    quiz_id = Column(String)
    topic = Column(String)
    difficulty = Column(String)
    total_questions = Column(Integer)
    correct_count = Column(Integer)
    score = Column(Float)
    answers = Column(Text) # Lưu trữ List[QuizAnswerRecord] dạng JSON
    completed_at = Column(DateTime, default=datetime.datetime.now)
