"""
conversation_store.py - Lưu trữ lịch sử chat vào file JSON
"""
import json
import os
from datetime import datetime
from typing import Dict, Optional
from models import Conversation, Message, MessageRole

CONVERSATIONS_FILE = "./data/conversations.json"

def _ensure_dir():
    os.makedirs("./data", exist_ok=True)

def _serialize_conversation(conv: Conversation) -> dict:
    return {
        "id": conv.id,
        "title": conv.title,
        "messages": [
            {
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in conv.messages
        ],
        "document_ids": conv.document_ids,
        "created_at": conv.created_at.isoformat(),
        "updated_at": conv.updated_at.isoformat()
    }

def _deserialize_conversation(data: dict) -> Conversation:
    messages = [
        Message(
            role=MessageRole(m["role"]),
            content=m["content"],
            timestamp=datetime.fromisoformat(m["timestamp"])
        )
        for m in data.get("messages", [])
    ]
    return Conversation(
        id=data["id"],
        title=data["title"],
        messages=messages,
        document_ids=data.get("document_ids", []),
        created_at=datetime.fromisoformat(data["created_at"]),
        updated_at=datetime.fromisoformat(data["updated_at"])
    )

def load_conversations() -> Dict[str, Conversation]:
    """Load tất cả conversations từ file JSON"""
    _ensure_dir()
    if not os.path.exists(CONVERSATIONS_FILE):
        return {}
    try:
        with open(CONVERSATIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {conv_id: _deserialize_conversation(conv_data) for conv_id, conv_data in data.items()}
    except Exception as e:
        print(f"Lỗi load conversations: {e}")
        return {}

def save_conversations(conversations: Dict[str, Conversation]):
    """Lưu tất cả conversations vào file JSON"""
    _ensure_dir()
    try:
        data = {conv_id: _serialize_conversation(conv) for conv_id, conv in conversations.items()}
        with open(CONVERSATIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Lỗi save conversations: {e}")

def save_single_conversation(conversations: Dict[str, Conversation], conv_id: str):
    """Lưu sau mỗi thay đổi (gọi từ main.py)"""
    save_conversations(conversations)
