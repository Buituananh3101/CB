"""
Script test API endpoints
Chạy: python test_api.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("\n=== Test Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

def test_upload_document(file_path):
    """Test upload document"""
    print("\n=== Test Upload Document ===")
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/api/documents/upload", files=files)
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
    return result.get('document_id')

def test_get_documents():
    """Test get all documents"""
    print("\n=== Test Get Documents ===")
    response = requests.get(f"{BASE_URL}/api/documents")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

def test_chat(message, document_ids=None):
    """Test chat endpoint"""
    print("\n=== Test Chat ===")
    data = {
        "message": message,
        "document_ids": document_ids or []
    }
    
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
    return result.get('conversation_id')

def test_create_mindmap(topic, document_ids=None):
    """Test create mindmap"""
    print("\n=== Test Create MindMap ===")
    data = {
        "topic": topic,
        "document_ids": document_ids or [],
        "depth": 3
    }
    
    response = requests.post(
        f"{BASE_URL}/api/mindmap",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

def test_create_note(title, document_ids=None):
    """Test create note"""
    print("\n=== Test Create Note ===")
    data = {
        "title": title,
        "document_ids": document_ids or [],
        "auto_generate": True
    }
    
    response = requests.post(
        f"{BASE_URL}/api/notes",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Note ID: {result.get('id')}")
    print(f"Content preview: {result.get('content', '')[:200]}...")
    return result.get('id')

def test_create_quiz(topic, document_ids=None):
    """Test create quiz"""
    print("\n=== Test Create Quiz ===")
    data = {
        "topic": topic,
        "num_questions": 3,
        "difficulty": "medium",
        "document_ids": document_ids or []
    }
    
    response = requests.post(
        f"{BASE_URL}/api/quiz",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Number of questions: {len(result.get('questions', []))}")
    
    if result.get('questions'):
        print(f"\nFirst question:")
        q = result['questions'][0]
        print(f"Q: {q.get('question')}")
        for opt in q.get('options', []):
            print(f"  {opt}")
        print(f"Correct: {q.get('options', [])[q.get('correct_answer', 0)]}")

def test_study_plan(topic, document_ids=None):
    """Test create study plan"""
    print("\n=== Test Create Study Plan ===")
    params = {"topic": topic}
    if document_ids:
        params["document_ids"] = document_ids
    
    response = requests.post(
        f"{BASE_URL}/api/study-plan",
        params=params
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Study Plan preview:\n{result.get('study_plan', '')[:500]}...")

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("MATH CHATBOT API - TEST SUITE")
    print("=" * 60)
    
    # 1. Health check
    test_health_check()
    
    # 2. Test basic chat (no documents)
    test_chat("Định lý Pythagoras là gì?")
    
    # 3. Test create mindmap
    test_create_mindmap("Hàm số bậc hai")
    
    # 4. Test create note
    test_create_note("Tổng hợp kiến thức về Đạo hàm")
    
    # 5. Test create quiz
    test_create_quiz("Phương trình bậc hai")
    
    # 6. Test study plan
    test_study_plan("Lượng giác cơ bản")
    
    # 7. Get all documents
    test_get_documents()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED!")
    print("=" * 60)

def interactive_test():
    """Interactive testing mode"""
    print("\n=== INTERACTIVE TEST MODE ===")
    print("1. Health Check")
    print("2. Upload Document")
    print("3. Chat")
    print("4. Create MindMap")
    print("5. Create Note")
    print("6. Create Quiz")
    print("7. Study Plan")
    print("8. Get Documents")
    print("9. Run All Tests")
    print("0. Exit")
    
    while True:
        choice = input("\nChọn test (0-9): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            test_health_check()
        elif choice == "2":
            file_path = input("Đường dẫn file: ").strip()
            test_upload_document(file_path)
        elif choice == "3":
            message = input("Tin nhắn: ").strip()
            test_chat(message)
        elif choice == "4":
            topic = input("Chủ đề: ").strip()
            test_create_mindmap(topic)
        elif choice == "5":
            title = input("Tiêu đề ghi chú: ").strip()
            test_create_note(title)
        elif choice == "6":
            topic = input("Chủ đề quiz: ").strip()
            test_create_quiz(topic)
        elif choice == "7":
            topic = input("Chủ đề kế hoạch học: ").strip()
            test_study_plan(topic)
        elif choice == "8":
            test_get_documents()
        elif choice == "9":
            run_all_tests()
        else:
            print("Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        run_all_tests()
    else:
        interactive_test()
