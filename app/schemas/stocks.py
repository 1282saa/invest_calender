from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any

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

class DisclosureResponse(BaseModel):
    """공시정보 응답"""
    corp_name: str
    corp_code: str
    stock_code: Optional[str] = None
    report_nm: str
    rcept_no: str
    flr_nm: str
    rcept_dt: str
    rm: Optional[str] = None
    corp_cls: str

class CompanyInfoResponse(BaseModel):
    """기업개황 응답"""
    corp_name: str
    corp_name_eng: Optional[str] = None
    stock_name: str
    stock_code: Optional[str] = None
    ceo_nm: str
    corp_cls: str
    adres: str
    hm_url: Optional[str] = None
    ir_url: Optional[str] = None
    phn_no: Optional[str] = None
    induty_code: str
    est_dt: str
    acc_mt: str

class DisclosureListResponse(BaseModel):
    """공시목록 응답"""
    success: bool
    data: List[DisclosureResponse] = []
    page_info: Optional[Dict[str, Any]] = None
    error: Optional[str] = None 