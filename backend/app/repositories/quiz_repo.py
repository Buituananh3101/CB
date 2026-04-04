"""
quiz_store.py — Lưu trữ lịch sử làm quiz vào Database PostgreSQL
"""
import json
from datetime import datetime
from typing import List, Dict, Optional

from app.core.database import SessionLocal
from app.models.db_models import DBQuizResult

def load_quiz_results() -> List[dict]:
    """Load tất cả kết quả quiz từ PostgreSQL"""
    db = SessionLocal()
    try:
        results = db.query(DBQuizResult).order_by(DBQuizResult.completed_at.desc()).all()
        quiz_list = []
        for r in results:
            quiz_list.append({
                "id": r.id,
                "quiz_id": r.quiz_id,
                "topic": r.topic,
                "difficulty": r.difficulty,
                "total_questions": r.total_questions,
                "correct_count": r.correct_count,
                "score": r.score,
                "completed_at": r.completed_at.isoformat(),
                "answers": json.loads(r.answers) if r.answers else []
            })
        return quiz_list
    except Exception as e:
        print(f"Lỗi load quiz results từ DB: {e}")
        return []
    finally:
        db.close()

def save_quiz_result(result: dict):
    """Lưu một kết quả quiz mới vào PostgreSQL"""
    db = SessionLocal()
    try:
        completed_at = result.get("completed_at")
        if isinstance(completed_at, str):
            completed_at = datetime.fromisoformat(completed_at)
        elif not completed_at:
            completed_at = datetime.now()

        db_result = DBQuizResult(
            id=result["id"],
            quiz_id=result.get("quiz_id"),
            topic=result.get("topic"),
            difficulty=result.get("difficulty"),
            total_questions=result.get("total_questions"),
            correct_count=result.get("correct_count"),
            score=result.get("score"),
            answers=json.dumps(result.get("answers", [])),
            completed_at=completed_at
        )
        db.add(db_result)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Lỗi save quiz result vào DB: {e}")
    finally:
        db.close()

def delete_quiz_result(result_id: str) -> bool:
    """Xóa một kết quả quiz theo ID từ PostgreSQL"""
    db = SessionLocal()
    try:
        deleted_count = db.query(DBQuizResult).filter(DBQuizResult.id == result_id).delete()
        db.commit()
        return deleted_count > 0
    except Exception as e:
        db.rollback()
        print(f"Lỗi xóa quiz result trong DB: {e}")
        return False
    finally:
        db.close()
