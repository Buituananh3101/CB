from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union
import os
import json

class Settings(BaseSettings):
    # API Keys
    GEMINI_API_KEY: str
    
    # Database
    DATABASE_URL: str = "sqlite:///./mathbot.db"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS CONFIGURATION (Đã sửa lỗi)
    ALLOWED_ORIGINS: Union[str, List[str]] = ["*"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: Union[str, List[str]]) -> List[str]:
        # Nếu giá trị là chuỗi (do đọc từ .env), ta sẽ xử lý nó
        if isinstance(v, str):
            if not v or v.strip() == "":
                return ["*"]
            
            # Trường hợp 1: Dạng JSON string '["http://..."]'
            if v.strip().startswith("["):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            
            # Trường hợp 2: Dạng chuỗi cách nhau dấu phẩy "http://..., http://..."
            return [origin.strip() for origin in v.split(",")]
            
        return v
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "./uploads"
    
    # Vector Store
    VECTOR_STORE_DIR: str = "./vector_store"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Tạo các thư mục cần thiết
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.VECTOR_STORE_DIR, exist_ok=True)