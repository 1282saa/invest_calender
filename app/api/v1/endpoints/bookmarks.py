from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.db.session import get_db
from app.db import models
from app.schemas.stocks import BookmarkCreate, BookmarkResponse
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[BookmarkResponse])
async def get_bookmarks(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """북마크 목록 조회"""
    bookmarks = db.query(models.Bookmark)\
        .filter(models.Bookmark.user_id == current_user.id)\
        .options(joinedload(models.Bookmark.event))\
        .offset(skip)\
        .limit(limit)\
        .all()
    return bookmarks

@router.post("/", response_model=BookmarkResponse)
async def create_bookmark(
    bookmark_in: BookmarkCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """북마크 추가"""
    # 이벤트 존재 확인
    event = db.query(models.CalendarEvent).filter(
        models.CalendarEvent.id == bookmark_in.event_id
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="이벤트를 찾을 수 없습니다.")
    
    # 중복 체크
    existing = db.query(models.Bookmark).filter(
        models.Bookmark.user_id == current_user.id,
        models.Bookmark.event_id == bookmark_in.event_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="이미 북마크한 이벤트입니다.")
    
    # 북마크 생성
    bookmark = models.Bookmark(
        user_id=current_user.id,
        event_id=bookmark_in.event_id,
        note=bookmark_in.note
    )
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    
    return bookmark

@router.delete("/{bookmark_id}")
async def delete_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """북마크 삭제"""
    bookmark = db.query(models.Bookmark).filter(
        models.Bookmark.id == bookmark_id,
        models.Bookmark.user_id == current_user.id
    ).first()
    
    if not bookmark:
        raise HTTPException(status_code=404, detail="북마크를 찾을 수 없습니다.")
    
    db.delete(bookmark)
    db.commit()
    
    return {"message": "북마크가 삭제되었습니다."} 