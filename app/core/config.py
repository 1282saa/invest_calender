from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # 기본 설정
    APP_NAME: str = "InvestCalendar"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 데이터베이스 설정
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./invest_calendar.db")
    
    # Redis 설정
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # JWT 설정
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # 한국투자증권 API 설정
    KIS_APP_KEY: str = os.getenv("KIS_APP_KEY", "")
    KIS_APP_SECRET: str = os.getenv("KIS_APP_SECRET", "")
    KIS_API_BASE_URL: str = os.getenv("KIS_API_BASE_URL", "https://openapi.koreainvestment.com:9443")
    KIS_ENV: str = os.getenv("KIS_ENV", "vts")  # vts: 모의투자, prod: 실전투자
    
    # Perplexity AI API 설정
    PERPLEXITY_API_KEY: str = os.getenv("PERPLEXITY_API_KEY", "")
    
    # DART(전자공시시스템) API 설정
    DART_API_KEY: str = os.getenv("DART_API_KEY", "")
    
    # CORS 설정
    CORS_ORIGINS: list = ["*"]
    
    # 로깅 설정
    LOG_LEVEL: str = "INFO"
    
    # 데이터 파이프라인 설정
    ENABLE_DATA_PIPELINE: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 