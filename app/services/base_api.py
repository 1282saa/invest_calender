"""
Base API Client - 공통 API 기능 제공
"""
import aiohttp
import asyncio
from typing import Dict, Any, Optional, TypeVar, Callable
from functools import wraps
import logging
from datetime import datetime, timedelta
import json
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

T = TypeVar('T')

class RateLimiter:
    """API 호출 속도 제한 관리"""
    def __init__(self, calls_per_second: int = 10):
        self.calls_per_second = calls_per_second
        self.call_times = []
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        async with self._lock:
            now = datetime.now()
            # 1초 이내의 호출만 유지
            self.call_times = [t for t in self.call_times if now - t < timedelta(seconds=1)]
            
            if len(self.call_times) >= self.calls_per_second:
                # 대기 시간 계산
                sleep_time = 1.0 - (now - self.call_times[0]).total_seconds()
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    self.call_times = []
            
            self.call_times.append(now)

def with_retry(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """재시도 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (backoff ** attempt)
                        logger.warning(
                            f"{func.__name__} 실패 (시도 {attempt + 1}/{max_retries}). "
                            f"{wait_time}초 후 재시도: {str(e)}"
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"{func.__name__} 최종 실패: {str(e)}")
                except Exception as e:
                    logger.error(f"{func.__name__} 예상치 못한 오류: {str(e)}")
                    raise
            
            raise last_exception
        return wrapper
    return decorator

def with_cache(ttl_seconds: int = 300):
    """캐싱 데코레이터"""
    cache = {}
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # 캐시 확인
            if cache_key in cache:
                cached_data, cached_time = cache[cache_key]
                if datetime.now() - cached_time < timedelta(seconds=ttl_seconds):
                    logger.debug(f"캐시 히트: {cache_key}")
                    return cached_data
            
            # 실제 함수 호출
            result = await func(*args, **kwargs)
            
            # 캐시 저장
            cache[cache_key] = (result, datetime.now())
            
            # 오래된 캐시 정리
            current_time = datetime.now()
            expired_keys = [
                k for k, (_, t) in cache.items() 
                if current_time - t > timedelta(seconds=ttl_seconds * 2)
            ]
            for key in expired_keys:
                del cache[key]
            
            return result
        return wrapper
    return decorator

class BaseAPIClient(ABC):
    """기본 API 클라이언트 추상 클래스"""
    
    def __init__(self, base_url: str, rate_limit: int = 10):
        self.base_url = base_url
        self.rate_limiter = RateLimiter(rate_limit)
        self._session: Optional[aiohttp.ClientSession] = None
        self.timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.mock_mode = False
        
    async def __aenter__(self):
        await self.init_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_session()
        
    async def init_session(self):
        """세션 초기화"""
        if not self._session or self._session.closed:
            connector = aiohttp.TCPConnector(
                limit=100,
                ttl_dns_cache=300,
                use_dns_cache=True
            )
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=self.timeout
            )
            
    async def close_session(self):
        """세션 종료"""
        if self._session and not self._session.closed:
            await self._session.close()
            
    async def get_session(self) -> aiohttp.ClientSession:
        """세션 반환"""
        if not self._session or self._session.closed:
            await self.init_session()
        return self._session
    
    @abstractmethod
    async def _get_headers(self, **kwargs) -> Dict[str, str]:
        """API별 헤더 생성 (구현 필요)"""
        pass
    
    @with_retry(max_retries=3, delay=1.0)
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """HTTP 요청 실행"""
        await self.rate_limiter.acquire()
        
        session = await self.get_session()
        url = f"{self.base_url}{endpoint}"
        
        request_kwargs = {
            'headers': headers or {},
            'params': params,
            **kwargs
        }
        
        if json_data:
            request_kwargs['json'] = json_data
            
        async with session.request(method, url, **request_kwargs) as response:
            response_text = await response.text()
            
            if response.status >= 400:
                logger.error(f"API 오류: {method} {url} - {response.status}: {response_text}")
                response.raise_for_status()
                
            try:
                return json.loads(response_text) if response_text else {}
            except json.JSONDecodeError:
                logger.error(f"JSON 파싱 오류: {response_text}")
                return {'error': 'Invalid JSON response', 'raw': response_text}
    
    async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """GET 요청"""
        return await self._make_request('GET', endpoint, **kwargs)
        
    async def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """POST 요청"""
        return await self._make_request('POST', endpoint, **kwargs)
        
    async def batch_request(
        self,
        requests: list[Dict[str, Any]],
        max_concurrent: int = 5
    ) -> list[Dict[str, Any]]:
        """배치 요청 처리"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_request(request_info):
            async with semaphore:
                method = request_info.get('method', 'GET')
                endpoint = request_info['endpoint']
                kwargs = {k: v for k, v in request_info.items() if k not in ['method', 'endpoint']}
                
                try:
                    return await self._make_request(method, endpoint, **kwargs)
                except Exception as e:
                    logger.error(f"배치 요청 실패: {endpoint} - {str(e)}")
                    return {'error': str(e), 'endpoint': endpoint}
        
        tasks = [process_request(req) for req in requests]
        return await asyncio.gather(*tasks)

class DataMapper:
    """API 응답 데이터 변환 도우미"""
    
    @staticmethod
    def safe_float(value: Any, default: float = 0.0) -> float:
        """안전한 float 변환"""
        try:
            return float(value) if value else default
        except (TypeError, ValueError):
            return default
            
    @staticmethod
    def safe_int(value: Any, default: int = 0) -> int:
        """안전한 int 변환"""
        try:
            return int(value) if value else default
        except (TypeError, ValueError):
            return default
            
    @staticmethod
    def format_date(date_str: str, input_format: str = "%Y%m%d", output_format: str = "%Y-%m-%d") -> str:
        """날짜 형식 변환"""
        try:
            return datetime.strptime(date_str, input_format).strftime(output_format)
        except:
            return date_str
            
    @classmethod
    def map_stock_price(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """주식 가격 데이터 매핑"""
        return {
            'current_price': cls.safe_float(data.get('stck_prpr')),
            'change_price': cls.safe_float(data.get('prdy_vrss')),
            'change_rate': cls.safe_float(data.get('prdy_ctrt')),
            'volume': cls.safe_int(data.get('acml_vol')),
            'high_price': cls.safe_float(data.get('stck_hgpr')),
            'low_price': cls.safe_float(data.get('stck_lwpr')),
            'opening_price': cls.safe_float(data.get('stck_oprc')),
            'stock_name': data.get('prdt_name', '')
        } 