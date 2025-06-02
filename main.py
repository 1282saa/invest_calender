from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.api.v1.api import api_router
from app.db.session import engine
from app.db import models
from app.core.scheduler import start_scheduler
from app.services.data_pipeline import start_data_pipeline, stop_data_pipeline

# 데이터베이스 테이블 생성
models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 실행
    start_scheduler()
    
    # 데이터 파이프라인 시작 (환경변수로 제어)
    if settings.ENABLE_DATA_PIPELINE:
        await start_data_pipeline()
    
    yield
    
    # 종료 시 실행
    if settings.ENABLE_DATA_PIPELINE:
        await stop_data_pipeline()

app = FastAPI(
    title="투자캘린더 - InvestCalendar",
    description="투자 초보를 위한 스마트 투자 일정 관리 서비스",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="static"), name="static")

# 템플릿 설정
templates = Jinja2Templates(directory="templates")

# API 라우터 등록
app.include_router(api_router, prefix="/api/v1")

# 메인 페이지 라우트
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "InvestCalendar"}
    )

# 헬스 체크
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "InvestCalendar"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 