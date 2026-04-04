"""
conversation_store.py - Lưu trữ lịch sử chat vào PostgreSQL
"""
import json
from datetime import datetime
from typing import Dict
from app.models.schemas import Conversation, Message, MessageRole

from app.core.database import SessionLocal
from app.models.db_models import DBConversation, DBMessage

def load_conversations() -> Dict[str, Conversation]:
    """Load tất cả conversations từ Database (thay vì file JSON)"""
    db = SessionLocal()
    try:
        db_convs = db.query(DBConversation).all()
        conversations = {}
        for db_conv in db_convs:
            # Parse document_ids
            try:
                document_ids = json.loads(db_conv.document_ids) if db_conv.document_ids else []
            except:
                document_ids = []
            
            # Khôi phục messages
            messages = []
            for m in db_conv.messages:
                messages.append(Message(
                    role=MessageRole(m.role),
                    content=m.content,
                    timestamp=m.timestamp
                ))
            
            # Sắp xếp messages theo thời gian
            messages.sort(key=lambda x: x.timestamp)
            
            conversations[db_conv.id] = Conversation(
                id=db_conv.id,
                title=db_conv.title,
                messages=messages,
                document_ids=document_ids,
                created_at=db_conv.created_at,
                updated_at=db_conv.updated_at
            )
        return conversations
    except Exception as e:
        print(f"Lỗi load conversations từ DB: {e}")
        return {}
    finally:
         db.close()

def save_conversations(conversations: Dict[str, Conversation]):
    """Đồng bộ toàn bộ dict vào Postgres"""
    db = SessionLocal()
    try:
        # Lấy danh sách ID hiện tại
        existing_ids = {c.id for c in db.query(DBConversation.id).all()}
        
        # Xóa các hội thoại không còn trong dict
        current_ids = set(conversations.keys())
        ids_to_delete = existing_ids - current_ids
        if ids_to_delete:
             db.query(DBConversation).filter(DBConversation.id.in_(ids_to_delete)).delete(synchronize_session=False)
             
        for conv_id, conv in conversations.items():
            db_conv = db.query(DBConversation).filter(DBConversation.id == conv_id).first()
            if not db_conv:
                db_conv = DBConversation(
                    id=conv.id,
                    title=conv.title,
                    document_ids=json.dumps(conv.document_ids),
                    created_at=conv.created_at,
                    updated_at=conv.updated_at
                )
                db.add(db_conv)
            else:
                db_conv.title = conv.title
                db_conv.updated_at = conv.updated_at
                db_conv.document_ids = json.dumps(conv.document_ids)
            
            # Đồng bộ tin nhắn
            db.query(DBMessage).filter(DBMessage.conversation_id == conv_id).delete()
            for msg in conv.messages:
                db_msg = DBMessage(
                    conversation_id=conv_id,
                    role=msg.role.value,
                    content=msg.content,
                    timestamp=msg.timestamp
                )
                db.add(db_msg)
                
        db.commit()
    except Exception as e:
        print(f"Lỗi save_conversations: {e}")
        db.rollback()
    finally:
        db.close()

def save_single_conversation(conversations: Dict[str, Conversation], conv_id: str):
    """Lưu sau mỗi thay đổi của 1 hội thoại cụ thể"""
    conv = conversations.get(conv_id)
    if not conv:
         return
         
    db = SessionLocal()
    try:
        db_conv = db.query(DBConversation).filter(DBConversation.id == conv_id).first()
        if not db_conv:
            db_conv = DBConversation(
                id=conv.id,
                title=conv.title,
                document_ids=json.dumps(conv.document_ids),
                created_at=conv.created_at,
                updated_at=conv.updated_at
            )
            db.add(db_conv)
        else:
            db_conv.title = conv.title
            db_conv.updated_at = conv.updated_at
            db_conv.document_ids = json.dumps(conv.document_ids)
            
        # Tối ưu: Xóa toàn bộ tin nhắn của conv này và thêm lại
        db.query(DBMessage).filter(DBMessage.conversation_id == conv_id).delete()
        for msg in conv.messages:
            db_msg = DBMessage(
                conversation_id=conv_id,
                role=msg.role.value,
                content=msg.content,
                timestamp=msg.timestamp
            )
            db.add(db_msg)
            
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Lỗi save_single_conversation: {e}")
    finally:
        db.close()
