from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class EventType(str, enum.Enum):
    EARNINGS = "earnings"  # 실적발표
    DIVIDEND = "dividend"  # 배당
    DISCLOSURE = "disclosure"  # 공시
    HOLIDAY = "holiday"  # 휴장일
    IPO = "ipo"  # 신규상장
    MEETING = "meeting"  # 주주총회
    SPLIT = "split"  # 액면분할
    ECONOMIC = "economic"  # 경제지표
    PERSONAL = "personal"  # 개인일정

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
    watchlist = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")
    personal_events = relationship("CalendarEvent", back_populates="user", cascade="all, delete-orphan")

class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_date = Column(DateTime, nullable=False, index=True)
    event_type = Column(SQLEnum(EventType), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    stock_code = Column(String(20), index=True)
    stock_name = Column(String(100))
    importance = Column(String(20), default="medium")  # high, medium, low
    source = Column(String(50))  # KIS, DART, KRX, etc.
    meta_data = Column(Text)  # JSON 형식의 추가 데이터
    
    # User specific events
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="personal_events")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookmarks = relationship("Bookmark", back_populates="event", cascade="all, delete-orphan")

class Bookmark(Base):
    __tablename__ = "bookmarks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("calendar_events.id"), nullable=False)
    note = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="bookmarks")
    event = relationship("CalendarEvent", back_populates="bookmarks")

class Watchlist(Base):
    __tablename__ = "watchlist"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_code = Column(String(20), nullable=False)
    stock_name = Column(String(100), nullable=False)
    target_price = Column(Float)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="watchlist")

class Stock(Base):
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(20), unique=True, nullable=False, index=True)
    stock_name = Column(String(100), nullable=False)
    market_type = Column(String(20))  # KOSPI, KOSDAQ
    sector = Column(String(100))
    current_price = Column(Float)
    price_updated_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 