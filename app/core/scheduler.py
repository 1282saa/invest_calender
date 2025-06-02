from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
import asyncio

from app.db.session import SessionLocal
from app.db import models
from app.services.kis_api_refactored import kis_api_client_refactored as kis_api_client
from app.services.dart_api import dart_api_client

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def sync_daily_events():
    """매일 실행되는 이벤트 동기화 작업"""
    logger.info("일일 이벤트 동기화 시작")
    
    db = SessionLocal()
    try:
        # 현재 연월 가져오기
        now = datetime.now()
        year = now.year
        month = now.month
        
        # 휴장일 동기화
        holidays = await kis_api_client.get_holidays(str(year))
        
        for holiday_date in holidays:
            date_obj = datetime.strptime(holiday_date, "%Y-%m-%d")
            
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
                    source="KIS"
                )
                db.add(event)
        
        db.commit()
        logger.info("일일 이벤트 동기화 완료")
        
    except Exception as e:
        logger.error(f"이벤트 동기화 중 오류: {str(e)}")
        db.rollback()
    finally:
        db.close()

async def update_stock_prices():
    """주식 가격 업데이트 작업"""
    logger.info("주식 가격 업데이트 시작")
    
    db = SessionLocal()
    try:
        # 관심 종목 리스트 가져오기
        watchlist_items = db.query(models.Watchlist).distinct(models.Watchlist.stock_code).all()
        
        for item in watchlist_items:
            try:
                # 현재가 조회
                price_info = await kis_api_client.get_stock_price(item.stock_code)
                
                if price_info:
                    # 주식 정보 업데이트
                    stock = db.query(models.Stock).filter(
                        models.Stock.stock_code == item.stock_code
                    ).first()
                    
                    if stock:
                        stock.current_price = float(price_info.get('stck_prpr', 0))
                        stock.price_updated_at = datetime.now()
                    else:
                        # 새로운 주식 정보 생성
                        stock = models.Stock(
                            stock_code=item.stock_code,
                            stock_name=item.stock_name,
                            current_price=float(price_info.get('stck_prpr', 0)),
                            price_updated_at=datetime.now()
                        )
                        db.add(stock)
                        
            except Exception as e:
                logger.error(f"주식 가격 업데이트 오류 ({item.stock_code}): {str(e)}")
                continue
        
        db.commit()
        logger.info("주식 가격 업데이트 완료")
        
    except Exception as e:
        logger.error(f"주식 가격 업데이트 중 오류: {str(e)}")
        db.rollback()
    finally:
        db.close()

def start_scheduler():
    """스케줄러 시작"""
    # 매일 오전 6시에 이벤트 동기화
    scheduler.add_job(
        sync_daily_events,
        CronTrigger(hour=6, minute=0),
        id="sync_daily_events",
        replace_existing=True
    )
    
    # 장 시작 전(오전 8시 30분)과 장 마감 후(오후 4시)에 주식 가격 업데이트
    scheduler.add_job(
        update_stock_prices,
        CronTrigger(hour=8, minute=30),
        id="update_stock_prices_morning",
        replace_existing=True
    )
    
    scheduler.add_job(
        update_stock_prices,
        CronTrigger(hour=16, minute=0),
        id="update_stock_prices_evening",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("스케줄러가 시작되었습니다")

def shutdown_scheduler():
    """스케줄러 종료"""
    scheduler.shutdown()
    logger.info("스케줄러가 종료되었습니다") 