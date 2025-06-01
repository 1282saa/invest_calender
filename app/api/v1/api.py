from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, bookmarks, watchlist, stocks

api_router = APIRouter()

# 각 엔드포인트 라우터 등록
api_router.include_router(auth.router, prefix="/auth", tags=["인증"])
api_router.include_router(users.router, prefix="/users", tags=["사용자"])
api_router.include_router(bookmarks.router, prefix="/bookmarks", tags=["북마크"])
api_router.include_router(watchlist.router, prefix="/watchlist", tags=["관심종목"])
api_router.include_router(stocks.router, prefix="/stocks", tags=["주식정보"]) 