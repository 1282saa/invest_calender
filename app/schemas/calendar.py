from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class EventTypeFilter(str, Enum):
    EARNINGS = "earnings"  # 실적발표
    DIVIDEND = "dividend"  # 배당
    DISCLOSURE = "disclosure"  # 공시
    HOLIDAY = "holiday"  # 휴장일
    IPO = "ipo"  # 신규상장
    MEETING = "meeting"  # 주주총회
    SPLIT = "split"  # 액면분할
    ECONOMIC = "economic"  # 경제지표
    PERSONAL = "personal"  # 개인일정


class CalendarEventBase(BaseModel):
    """캘린더 이벤트 기본 스키마"""
    event_date: datetime
    title: str
    description: Optional[str] = None
    stock_code: Optional[str] = None
    stock_name: Optional[str] = None
    importance: Optional[str] = "medium"  # high, medium, low
    source: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None


class CalendarEventCreate(CalendarEventBase):
    """캘린더 이벤트 생성 스키마"""
    pass


class CalendarEventUpdate(BaseModel):
    """캘린더 이벤트 업데이트 스키마"""
    event_date: Optional[datetime] = None
    title: Optional[str] = None
    description: Optional[str] = None
    importance: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None


class CalendarEventResponse(CalendarEventBase):
    """캘린더 이벤트 응답 스키마"""
    id: int
    event_type: str
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    is_bookmarked: Optional[bool] = False

    class Config:
        orm_mode = True


class UpcomingEvent(BaseModel):
    """다가오는 이벤트 스키마"""
    id: int
    title: str
    event_date: datetime
    event_type: str
    importance: str
    stock_code: Optional[str] = None
    stock_name: Optional[str] = None


class UpcomingEventResponse(BaseModel):
    """다가오는 이벤트 응답 스키마"""
    today: List[UpcomingEvent] = []
    tomorrow: List[UpcomingEvent] = []
    this_week: List[UpcomingEvent] = []
    next_week: List[UpcomingEvent] = []


class CalendarFilters(BaseModel):
    """캘린더 필터 스키마"""
    event_types: Optional[List[EventTypeFilter]] = None
    stock_codes: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    bookmarked_only: bool = False 