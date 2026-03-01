import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ Lỗi: Chưa tìm thấy GEMINI_API_KEY trong file .env")
else:
    genai.configure(api_key=api_key)
    print(f"✅ Đang kiểm tra với Key: {api_key[:10]}...")
    
    try:
        print("\nDanh sách các Model khả dụng:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"\n❌ Lỗi kết nối: {e}")