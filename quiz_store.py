"""
quiz_store.py — Lưu trữ lịch sử làm quiz vào file JSON
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

QUIZ_RESULTS_FILE = "./data/quiz_results.json"


def _ensure_dir():
    os.makedirs("./data", exist_ok=True)


def load_quiz_results() -> List[dict]:
    """Load tất cả kết quả quiz từ file JSON"""
    _ensure_dir()
    if not os.path.exists(QUIZ_RESULTS_FILE):
        return []
    try:
        with open(QUIZ_RESULTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Lỗi load quiz results: {e}")
        return []


def save_quiz_result(result: dict):
    """Lưu một kết quả quiz mới vào file JSON"""
    _ensure_dir()
    results = load_quiz_results()
    results.insert(0, result)   # mới nhất lên đầu
    try:
        with open(QUIZ_RESULTS_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Lỗi save quiz result: {e}")


def delete_quiz_result(result_id: str) -> bool:
    """Xóa một kết quả quiz theo ID"""
    results = load_quiz_results()
    new_results = [r for r in results if r.get("id") != result_id]
    if len(new_results) == len(results):
        return False
    try:
        with open(QUIZ_RESULTS_FILE, "w", encoding="utf-8") as f:
            json.dump(new_results, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Lỗi xóa quiz result: {e}")
        return False
