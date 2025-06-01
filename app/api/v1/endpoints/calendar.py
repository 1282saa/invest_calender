from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import json

from app.db.session import get_db
from app.db import models
from app.schemas.calendar import (
    CalendarEventResponse, 
    CalendarEventCreate,
    CalendarEventUpdate,
    EventTypeFilter
)
from app.services.kis_api import kis_api_client
from app.api.deps import get_current_user_optional, get_current_user

router = APIRouter()

@router.get("/events", response_model=List[CalendarEventResponse])
async def get_calendar_events(
    start_date: datetime = Query(..., description="시작 날짜"),
    end_date: datetime = Query(..., description="종료 날짜"),
    event_types: Optional[List[EventTypeFilter]] = Query(None, description="이벤트 타입 필터"),
    stock_codes: Optional[List[str]] = Query(None, description="종목 코드 필터"),
    bookmarked_only: bool = Query(False, description="북마크된 이벤트만"),
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional)
):
    """캘린더 이벤트 조회"""
    
    # 기본 쿼리
    query = db.query(models.CalendarEvent).filter(
        models.CalendarEvent.event_date >= start_date,
        models.CalendarEvent.event_date <= end_date
    )
    
    # 이벤트 타입 필터
    if event_types:
        query = query.filter(models.CalendarEvent.event_type.in_(event_types))
    
    # 종목 코드 필터
    if stock_codes:
        query = query.filter(models.CalendarEvent.stock_code.in_(stock_codes))
    
    # 북마크 필터 (로그인한 경우)
    if bookmarked_only and current_user:
        bookmarked_event_ids = db.query(models.Bookmark.event_id).filter(
            models.Bookmark.user_id == current_user.id
        ).subquery()
        query = query.filter(models.CalendarEvent.id.in_(bookmarked_event_ids))
    
    # 개인 이벤트 포함 (로그인한 경우)
    if current_user:
        query = query.filter(
            (models.CalendarEvent.user_id == None) | 
            (models.CalendarEvent.user_id == current_user.id)
        )
    else:
        query = query.filter(models.CalendarEvent.user_id == None)
    
    events = query.order_by(models.CalendarEvent.event_date).all()
    
    # 북마크 상태 추가
    if current_user:
        bookmarked_ids = set(
            db.query(models.Bookmark.event_id)
            .filter(models.Bookmark.user_id == current_user.id)
            .scalar_all()
        )
        for event in events:
            event.is_bookmarked = event.id in bookmarked_ids
    
    return events

@router.post("/events/sync")
async def sync_calendar_events(
    year: int = Query(..., description="동기화할 연도"),
    month: int = Query(..., description="동기화할 월"),
    db: Session = Depends(get_db)
):
    """외부 API에서 캘린더 이벤트 동기화"""
    
    try:
        # 휴장일 동기화
        holidays = await kis_api_client.get_holidays(str(year))
        
        for holiday_date in holidays:
            # 해당 월의 휴장일만 처리
            date_obj = datetime.strptime(holiday_date, "%Y-%m-%d")
            if date_obj.month == month:
                # 중복 체크
                existing = db.query(models.CalendarEvent).filter(
                    models.CalendarEvent.event_date == date_obj,
                    models.CalendarEvent.event_type == models.EventType.HOLIDAY
                ).first()
                
                if not existing:
                    event = models.CalendarEvent(
                        event_date=date_obj,
                        event_type=models.EventType.HOLIDAY,
                        title="증시 휴장일",
                        description="한국 증시 휴장일입니다.",
                        importance="high",
                        source="KRX"
                    )
                    db.add(event)
        
        # 실적 발표 일정 동기화
        earnings = await kis_api_client.get_earnings_calendar(f"{year}-{month:02d}")
        
        for earning in earnings:
            date_obj = datetime.strptime(earning['date'], "%Y-%m-%d")
            
            # 중복 체크
            existing = db.query(models.CalendarEvent).filter(
                models.CalendarEvent.event_date == date_obj,
                models.CalendarEvent.stock_code == earning.get('stock_code'),
                models.CalendarEvent.event_type == models.EventType.EARNINGS
            ).first()
            
            if not existing:
                event = models.CalendarEvent(
                    event_date=date_obj,
                    event_type=models.EventType.EARNINGS,
                    title=f"{earning['company_name']} {earning['event_type']}",
                    description=earning.get('description', ''),
                    stock_code=earning.get('stock_code'),
                    stock_name=earning['company_name'],
                    importance="high",
                    source="KIS",
                    meta_data=json.dumps(earning)
                )
                db.add(event)
        
        db.commit()
        
        return {"message": f"{year}년 {month}월 이벤트 동기화 완료"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"동기화 중 오류 발생: {str(e)}")

@router.post("/events", response_model=CalendarEventResponse)
async def create_personal_event(
    event: CalendarEventCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """개인 캘린더 이벤트 생성"""
    
    db_event = models.CalendarEvent(
        **event.dict(),
        user_id=current_user.id,
        event_type=models.EventType.PERSONAL
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    return db_event

@router.put("/events/{event_id}", response_model=CalendarEventResponse)
async def update_personal_event(
    event_id: int,
    event_update: CalendarEventUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """개인 캘린더 이벤트 수정"""
    
    db_event = db.query(models.CalendarEvent).filter(
        models.CalendarEvent.id == event_id,
        models.CalendarEvent.user_id == current_user.id
    ).first()
    
    if not db_event:
        raise HTTPException(status_code=404, detail="이벤트를 찾을 수 없습니다.")
    
    for field, value in event_update.dict(exclude_unset=True).items():
        setattr(db_event, field, value)
    
    db.commit()
    db.refresh(db_event)
    
    return db_event

@router.delete("/events/{event_id}")
async def delete_personal_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """개인 캘린더 이벤트 삭제"""
    
    db_event = db.query(models.CalendarEvent).filter(
        models.CalendarEvent.id == event_id,
        models.CalendarEvent.user_id == current_user.id
    ).first()
    
    if not db_event:
        raise HTTPException(status_code=404, detail="이벤트를 찾을 수 없습니다.")
    
    db.delete(db_event)
    db.commit()
    
    return {"message": "이벤트가 삭제되었습니다."} 