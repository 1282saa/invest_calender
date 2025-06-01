from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class StockPriceResponse(BaseModel):
    """주식 현재가 응답"""
    stock_code: str
    stock_name: str
    current_price: float
    change_price: float
    change_rate: float
    volume: int
    high_price: float
    low_price: float
    opening_price: float
    previous_close: float

class StockHistoryResponse(BaseModel):
    """주식 기간별 시세 응답"""
    date: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    change_rate: float

class MarketIndexResponse(BaseModel):
    """시장 지수 응답"""
    index_code: str
    index_name: str
    current_value: float
    change_value: float
    change_rate: float
    high_value: float
    low_value: float

class InvestorTrendResponse(BaseModel):
    """투자자별 매매 동향 응답"""
    investor_type: str
    buy_amount: int
    sell_amount: int
    net_amount: int
    buy_volume: int
    sell_volume: int
    net_volume: int

class ProgramTradeResponse(BaseModel):
    """프로그램 매매 동향 응답"""
    stock_code: str
    stock_name: str
    program_buy_amount: int
    program_sell_amount: int
    program_net_amount: int
    program_buy_volume: int
    program_sell_volume: int
    program_net_volume: int

class StockSearchResponse(BaseModel):
    """종목 검색 응답"""
    stock_code: str
    stock_name: str
    market: str

class BookmarkCreate(BaseModel):
    """북마크 생성"""
    event_id: int
    note: Optional[str] = None

class BookmarkResponse(BaseModel):
    """북마크 응답"""
    id: int
    event_id: int
    note: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class WatchlistItemCreate(BaseModel):
    """관심종목 생성"""
    stock_code: str
    stock_name: str
    target_price: Optional[float] = None
    note: Optional[str] = None

class WatchlistItemUpdate(BaseModel):
    """관심종목 수정"""
    target_price: Optional[float] = None
    note: Optional[str] = None

class WatchlistItemResponse(BaseModel):
    """관심종목 응답"""
    id: int
    stock_code: str
    stock_name: str
    target_price: Optional[float] = None
    note: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True 