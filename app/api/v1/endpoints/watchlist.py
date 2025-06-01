from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.db import models
from app.schemas.stocks import WatchlistItemCreate, WatchlistItemUpdate, WatchlistItemResponse
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[WatchlistItemResponse])
async def get_watchlist(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """관심종목 목록 조회"""
    watchlist = db.query(models.Watchlist)\
        .filter(models.Watchlist.user_id == current_user.id)\
        .all()
    return watchlist

@router.post("/", response_model=WatchlistItemResponse)
async def add_to_watchlist(
    item_in: WatchlistItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """관심종목 추가"""
    # 중복 체크
    existing = db.query(models.Watchlist).filter(
        models.Watchlist.user_id == current_user.id,
        models.Watchlist.stock_code == item_in.stock_code
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="이미 관심종목에 추가된 종목입니다.")
    
    # 관심종목 추가
    watchlist_item = models.Watchlist(
        user_id=current_user.id,
        **item_in.dict()
    )
    db.add(watchlist_item)
    db.commit()
    db.refresh(watchlist_item)
    
    return watchlist_item

@router.put("/{item_id}", response_model=WatchlistItemResponse)
async def update_watchlist_item(
    item_id: int,
    item_update: WatchlistItemUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """관심종목 수정"""
    item = db.query(models.Watchlist).filter(
        models.Watchlist.id == item_id,
        models.Watchlist.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="관심종목을 찾을 수 없습니다.")
    
    for field, value in item_update.dict(exclude_unset=True).items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    
    return item

@router.delete("/{item_id}")
async def remove_from_watchlist(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """관심종목 삭제"""
    item = db.query(models.Watchlist).filter(
        models.Watchlist.id == item_id,
        models.Watchlist.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="관심종목을 찾을 수 없습니다.")
    
    db.delete(item)
    db.commit()
    
    return {"message": "관심종목에서 삭제되었습니다."} 