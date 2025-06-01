from fastapi import APIRouter, Depends
from app.api.deps import get_current_active_user
from app.db import models
from app.schemas.auth import UserResponse

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: models.User = Depends(get_current_active_user)
):
    """현재 로그인한 사용자 정보 조회"""
    return current_user 