"""
데이터 파이프라인 서비스
여러 API로부터 데이터를 효율적으로 수집, 변환, 저장하는 서비스
"""
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import json

from app.services.kis_api_refactored import kis_api_client_refactored
from app.services.dart_api import dart_api_client
from app.services.perplexity_api import perplexity_client
from app.db.session import SessionLocal
from app.db import models
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class DataSource(Enum):
    """데이터 소스 열거형"""
    KIS = "kis"
    DART = "dart"
    PERPLEXITY = "perplexity"
    UPBIT = "upbit"
    
class DataType(Enum):
    """데이터 타입 열거형"""
    STOCK_PRICE = "stock_price"
    STOCK_HISTORY = "stock_history"
    MARKET_INDEX = "market_index"
    DISCLOSURE = "disclosure"
    NEWS = "news"
    CRYPTO = "crypto"
    EXCHANGE_RATE = "exchange_rate"

@dataclass
class DataRequest:
    """데이터 요청 정보"""
    data_type: DataType
    source: DataSource
    params: Dict[str, Any]
    priority: int = 5  # 1-10, 낮을수록 우선순위 높음
    
@dataclass
class DataResponse:
    """데이터 응답 정보"""
    request: DataRequest
    data: Optional[Any]
    error: Optional[str] = None
    fetched_at: datetime = None
    
    def __post_init__(self):
        if not self.fetched_at:
            self.fetched_at = datetime.now()

class DataPipeline:
    """데이터 수집 및 처리 파이프라인"""
    
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self._queue = asyncio.PriorityQueue()
        self._workers = []
        self._running = False
        
    async def start(self):
        """파이프라인 시작"""
        if self._running:
            return
            
        self._running = True
        
        # 워커 시작
        for i in range(self.max_concurrent):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self._workers.append(worker)
            
        logger.info(f"데이터 파이프라인 시작: {self.max_concurrent}개 워커")
        
    async def stop(self):
        """파이프라인 중지"""
        self._running = False
        
        # 모든 워커 종료 대기
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()
        
        logger.info("데이터 파이프라인 중지")
        
    async def _worker(self, name: str):
        """워커 프로세스"""
        logger.info(f"{name} 시작")
        
        while self._running:
            try:
                # 큐에서 작업 가져오기 (타임아웃 1초)
                priority, request = await asyncio.wait_for(
                    self._queue.get(), 
                    timeout=1.0
                )
                
                # 데이터 수집 실행
                response = await self._fetch_data(request)
                
                # 데이터 처리
                await self._process_data(response)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"{name} 오류: {str(e)}")
                
        logger.info(f"{name} 종료")
        
    async def _fetch_data(self, request: DataRequest) -> DataResponse:
        """데이터 수집 실행"""
        try:
            data = None
            
            # KIS API
            if request.source == DataSource.KIS:
                data = await self._fetch_kis_data(request)
                
            # DART API
            elif request.source == DataSource.DART:
                data = await self._fetch_dart_data(request)
                
            # Perplexity API
            elif request.source == DataSource.PERPLEXITY:
                data = await self._fetch_perplexity_data(request)
                
            # Upbit API
            elif request.source == DataSource.UPBIT:
                data = await self._fetch_upbit_data(request)
                
            return DataResponse(request=request, data=data)
            
        except Exception as e:
            logger.error(f"데이터 수집 실패: {request.data_type.value} - {str(e)}")
            return DataResponse(request=request, data=None, error=str(e))
            
    async def _fetch_kis_data(self, request: DataRequest) -> Any:
        """KIS API 데이터 수집"""
        async with kis_api_client_refactored as client:
            if request.data_type == DataType.STOCK_PRICE:
                if 'stock_codes' in request.params:
                    # 다중 종목 조회
                    return await client.get_multiple_stock_prices(
                        request.params['stock_codes']
                    )
                else:
                    # 단일 종목 조회
                    return await client.get_stock_price(
                        request.params['stock_code']
                    )
                    
            elif request.data_type == DataType.STOCK_HISTORY:
                return await client.get_stock_history(
                    request.params['stock_code'],
                    request.params['start_date'],
                    request.params['end_date'],
                    request.params.get('period_type', 'D')
                )
                
            elif request.data_type == DataType.MARKET_INDEX:
                return await client.get_market_indices()
                
    async def _fetch_dart_data(self, request: DataRequest) -> Any:
        """DART API 데이터 수집"""
        if request.data_type == DataType.DISCLOSURE:
            if 'corp_code' in request.params:
                # 특정 기업 공시
                return await dart_api_client.get_company_info(
                    request.params['corp_code']
                )
            else:
                # 최근 공시 목록
                return await dart_api_client.get_recent_disclosures(
                    request.params.get('corp_cls', 'Y'),
                    request.params.get('days', 7),
                    request.params.get('important_only', True)
                )
                
    async def _fetch_perplexity_data(self, request: DataRequest) -> Any:
        """Perplexity API 데이터 수집"""
        if request.data_type == DataType.NEWS:
            if 'event_title' in request.params:
                return await perplexity_client.explain_market_event(
                    request.params['event_title'],
                    request.params.get('event_details', '')
                )
            else:
                return await perplexity_client.get_daily_market_summary()
                
    async def _fetch_upbit_data(self, request: DataRequest) -> Any:
        """Upbit API 데이터 수집"""
        if request.data_type == DataType.CRYPTO:
            symbol = request.params.get('symbol', 'BTC')
            
            async with aiohttp.ClientSession() as session:
                url = f"https://api.upbit.com/v1/ticker?markets=KRW-{symbol}"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data[0] if data else None
                        
    async def _process_data(self, response: DataResponse):
        """수집된 데이터 처리"""
        if response.error or not response.data:
            return
            
        # 데이터 타입별 처리
        if response.request.data_type == DataType.STOCK_PRICE:
            await self._save_stock_prices(response.data)
        elif response.request.data_type == DataType.DISCLOSURE:
            await self._save_disclosures(response.data)
            
    async def _save_stock_prices(self, data: Union[Dict, List[Dict]]):
        """주식 가격 데이터 저장"""
        db = SessionLocal()
        try:
            if isinstance(data, dict) and 'stock_code' not in data:
                # 다중 종목 데이터
                for stock_code, price_data in data.items():
                    self._update_stock_price(db, stock_code, price_data)
            else:
                # 단일 종목 데이터
                stock_code = data.get('stock_code', '')
                if stock_code:
                    self._update_stock_price(db, stock_code, data)
                    
            db.commit()
            
        except Exception as e:
            logger.error(f"주식 가격 저장 실패: {str(e)}")
            db.rollback()
        finally:
            db.close()
            
    def _update_stock_price(self, db: Session, stock_code: str, price_data: Dict):
        """주식 가격 업데이트"""
        stock = db.query(models.Stock).filter(
            models.Stock.stock_code == stock_code
        ).first()
        
        if stock:
            stock.current_price = price_data.get('current_price', 0)
            stock.price_updated_at = datetime.now()
        else:
            stock = models.Stock(
                stock_code=stock_code,
                stock_name=price_data.get('stock_name', ''),
                current_price=price_data.get('current_price', 0),
                price_updated_at=datetime.now()
            )
            db.add(stock)
            
    async def _save_disclosures(self, data: Union[Dict, List[Dict]]):
        """공시 데이터 저장"""
        # 구현 필요
        pass
        
    async def add_request(self, request: DataRequest):
        """데이터 요청 추가"""
        await self._queue.put((request.priority, request))
        
    async def add_batch_requests(self, requests: List[DataRequest]):
        """배치 데이터 요청 추가"""
        for request in requests:
            await self.add_request(request)
            
    def create_stock_price_requests(
        self, 
        stock_codes: List[str], 
        batch_size: int = 10
    ) -> List[DataRequest]:
        """주식 가격 요청 생성"""
        requests = []
        
        # 배치로 나누기
        for i in range(0, len(stock_codes), batch_size):
            batch = stock_codes[i:i + batch_size]
            
            request = DataRequest(
                data_type=DataType.STOCK_PRICE,
                source=DataSource.KIS,
                params={'stock_codes': batch},
                priority=3
            )
            requests.append(request)
            
        return requests
        
    def create_market_overview_requests(self) -> List[DataRequest]:
        """시장 전체 개요 요청 생성"""
        return [
            # 시장 지수
            DataRequest(
                data_type=DataType.MARKET_INDEX,
                source=DataSource.KIS,
                params={},
                priority=1
            ),
            # 일일 시장 요약
            DataRequest(
                data_type=DataType.NEWS,
                source=DataSource.PERPLEXITY,
                params={},
                priority=2
            ),
            # 최근 중요 공시
            DataRequest(
                data_type=DataType.DISCLOSURE,
                source=DataSource.DART,
                params={'days': 1, 'important_only': True},
                priority=2
            ),
            # 주요 가상화폐
            DataRequest(
                data_type=DataType.CRYPTO,
                source=DataSource.UPBIT,
                params={'symbol': 'BTC'},
                priority=4
            ),
            DataRequest(
                data_type=DataType.CRYPTO,
                source=DataSource.UPBIT,
                params={'symbol': 'ETH'},
                priority=4
            )
        ]

# 전역 파이프라인 인스턴스
data_pipeline = DataPipeline(max_concurrent=5)

# 스케줄러 함수
async def scheduled_data_collection():
    """정기적인 데이터 수집"""
    # 인기 종목 리스트
    top_stocks = [
        "005930", "000660", "035720", "035420", "051910",
        "006400", "207940", "068270", "373220", "005380"
    ]
    
    # 주식 가격 요청 생성
    stock_requests = data_pipeline.create_stock_price_requests(top_stocks)
    
    # 시장 개요 요청 생성
    market_requests = data_pipeline.create_market_overview_requests()
    
    # 모든 요청 추가
    all_requests = stock_requests + market_requests
    await data_pipeline.add_batch_requests(all_requests)
    
    logger.info(f"스케줄된 데이터 수집: {len(all_requests)}개 요청")

# 파이프라인 시작/중지 함수
async def start_data_pipeline():
    """데이터 파이프라인 시작"""
    await data_pipeline.start()
    
    # 정기 수집 스케줄링 (예: 5분마다)
    async def periodic_collection():
        while True:
            try:
                await scheduled_data_collection()
                await asyncio.sleep(300)  # 5분
            except Exception as e:
                logger.error(f"정기 수집 오류: {str(e)}")
                await asyncio.sleep(60)  # 오류 시 1분 대기
                
    asyncio.create_task(periodic_collection())
    
async def stop_data_pipeline():
    """데이터 파이프라인 중지"""
    await data_pipeline.stop() 