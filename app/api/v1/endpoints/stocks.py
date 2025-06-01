from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import asyncio

from app.db.session import get_db
from app.db import models
from app.services.kis_api import kis_api_client
from app.services.perplexity_api import perplexity_client
from app.api.deps import get_current_user_optional
from app.schemas.stocks import (
    StockPriceResponse,
    StockHistoryResponse,
    MarketIndexResponse,
    InvestorTrendResponse,
    ProgramTradeResponse,
    StockSearchResponse
)

router = APIRouter()

@router.get("/price/{stock_code}", response_model=StockPriceResponse)
async def get_stock_price(
    stock_code: str,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional)
):
    """주식 현재가 조회"""
    try:
        # KIS API에서 현재가 조회
        price_data = await kis_api_client.get_stock_price(stock_code)
        
        if not price_data:
            raise HTTPException(status_code=404, detail="종목 정보를 찾을 수 없습니다.")
        
        # 주식 정보 업데이트 또는 생성
        stock = db.query(models.Stock).filter(
            models.Stock.stock_code == stock_code
        ).first()
        
        if stock:
            stock.current_price = float(price_data.get('stck_prpr', 0))
            stock.price_updated_at = datetime.now()
        else:
            stock = models.Stock(
                stock_code=stock_code,
                stock_name=price_data.get('prdt_name', ''),
                current_price=float(price_data.get('stck_prpr', 0)),
                price_updated_at=datetime.now()
            )
            db.add(stock)
        
        db.commit()
        
        return StockPriceResponse(
            stock_code=stock_code,
            stock_name=price_data.get('prdt_name', ''),
            current_price=float(price_data.get('stck_prpr', 0)),
            change_price=float(price_data.get('prdy_vrss', 0)),
            change_rate=float(price_data.get('prdy_ctrt', 0)),
            volume=int(price_data.get('acml_vol', 0)),
            high_price=float(price_data.get('stck_hgpr', 0)),
            low_price=float(price_data.get('stck_lwpr', 0)),
            opening_price=float(price_data.get('stck_oprc', 0)),
            previous_close=float(price_data.get('stck_prpr', 0)) - float(price_data.get('prdy_vrss', 0))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"주식 정보 조회 중 오류: {str(e)}")

@router.get("/history/{stock_code}", response_model=List[StockHistoryResponse])
async def get_stock_history(
    stock_code: str,
    start_date: datetime = Query(..., description="시작일"),
    end_date: datetime = Query(..., description="종료일"),
    period_type: str = Query("D", description="기간 타입: D(일), W(주), M(월), Y(년)"),
    db: Session = Depends(get_db)
):
    """주식 기간별 시세 조회"""
    try:
        history_data = await kis_api_client.get_stock_history(
            stock_code,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d"),
            period_type
        )
        
        if not history_data:
            return []
        
        result = []
        for item in history_data:
            result.append(StockHistoryResponse(
                date=f"{item['stck_bsop_date'][:4]}-{item['stck_bsop_date'][4:6]}-{item['stck_bsop_date'][6:8]}",
                open_price=float(item.get('stck_oprc', 0)),
                high_price=float(item.get('stck_hgpr', 0)),
                low_price=float(item.get('stck_lwpr', 0)),
                close_price=float(item.get('stck_clpr', 0)),
                volume=int(item.get('acml_vol', 0)),
                change_rate=float(item.get('prdy_ctrt', 0))
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"기간별 시세 조회 중 오류: {str(e)}")

@router.get("/market-index", response_model=List[MarketIndexResponse])
async def get_market_indices():
    """주요 시장 지수 조회"""
    try:
        # KOSPI, KOSDAQ 지수 동시 조회
        kospi_task = kis_api_client.get_market_index("0001")
        kosdaq_task = kis_api_client.get_market_index("1001")
        
        kospi_data, kosdaq_data = await asyncio.gather(kospi_task, kosdaq_task)
        
        result = []
        
        if kospi_data:
            result.append(MarketIndexResponse(
                index_code="0001",
                index_name="KOSPI",
                current_value=float(kospi_data.get('bstp_nmix_prpr', 0)),
                change_value=float(kospi_data.get('bstp_nmix_prdy_vrss', 0)),
                change_rate=float(kospi_data.get('bstp_nmix_prdy_ctrt', 0)),
                high_value=float(kospi_data.get('bstp_nmix_hgpr', 0)),
                low_value=float(kospi_data.get('bstp_nmix_lwpr', 0))
            ))
        
        if kosdaq_data:
            result.append(MarketIndexResponse(
                index_code="1001",
                index_name="KOSDAQ",
                current_value=float(kosdaq_data.get('bstp_nmix_prpr', 0)),
                change_value=float(kosdaq_data.get('bstp_nmix_prdy_vrss', 0)),
                change_rate=float(kosdaq_data.get('bstp_nmix_prdy_ctrt', 0)),
                high_value=float(kosdaq_data.get('bstp_nmix_hgpr', 0)),
                low_value=float(kosdaq_data.get('bstp_nmix_lwpr', 0))
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"시장 지수 조회 중 오류: {str(e)}")

@router.get("/investor-trend/{stock_code}", response_model=List[InvestorTrendResponse])
async def get_investor_trend(
    stock_code: str
):
    """투자자별 매매 동향 조회"""
    try:
        trend_data = await kis_api_client.get_investor_trend(stock_code)
        
        if not trend_data:
            return []
        
        result = []
        investor_types = {
            "1": "개인",
            "2": "외국인",
            "3": "기관계",
            "4": "금융투자",
            "5": "보험",
            "6": "투신",
            "7": "기타금융",
            "8": "은행",
            "9": "연기금등",
            "B": "기타법인",
            "P": "개인"
        }
        
        for item in trend_data:
            investor_type = investor_types.get(item.get('invr_cd', ''), "기타")
            result.append(InvestorTrendResponse(
                investor_type=investor_type,
                buy_amount=int(item.get('buy_amt', 0)),
                sell_amount=int(item.get('sell_amt', 0)),
                net_amount=int(item.get('net_amt', 0)),
                buy_volume=int(item.get('buy_qty', 0)),
                sell_volume=int(item.get('sell_qty', 0)),
                net_volume=int(item.get('net_qty', 0))
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"투자자별 매매 동향 조회 중 오류: {str(e)}")

@router.get("/program-trade", response_model=List[ProgramTradeResponse])
async def get_program_trade():
    """프로그램 매매 동향 조회"""
    try:
        trade_data = await kis_api_client.get_program_trade()
        
        if not trade_data:
            return []
        
        result = []
        for item in trade_data[:20]:  # 상위 20개만
            result.append(ProgramTradeResponse(
                stock_code=item.get('stck_shrn_iscd', ''),
                stock_name=item.get('hts_kor_isnm', ''),
                program_buy_amount=int(item.get('pgmg_buy_amt', 0)),
                program_sell_amount=int(item.get('pgmg_sell_amt', 0)),
                program_net_amount=int(item.get('pgmg_net_amt', 0)),
                program_buy_volume=int(item.get('pgmg_buy_qty', 0)),
                program_sell_volume=int(item.get('pgmg_sell_qty', 0)),
                program_net_volume=int(item.get('pgmg_net_qty', 0))
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"프로그램 매매 동향 조회 중 오류: {str(e)}")

@router.get("/search", response_model=List[StockSearchResponse])
async def search_stocks(
    keyword: str = Query(..., description="검색 키워드"),
    db: Session = Depends(get_db)
):
    """종목 검색"""
    try:
        # KIS API에서 검색 (현재는 mock 데이터)
        search_results = await kis_api_client.search_stock(keyword)
        
        # DB에서도 검색
        db_results = db.query(models.Stock).filter(
            models.Stock.stock_name.contains(keyword)
        ).limit(10).all()
        
        # 결과 병합
        result_dict = {}
        
        for item in search_results:
            result_dict[item['stock_code']] = StockSearchResponse(
                stock_code=item['stock_code'],
                stock_name=item['stock_name'],
                market=item.get('market', 'KOSPI')
            )
        
        for stock in db_results:
            if stock.stock_code not in result_dict:
                result_dict[stock.stock_code] = StockSearchResponse(
                    stock_code=stock.stock_code,
                    stock_name=stock.stock_name,
                    market=stock.market_type or 'KOSPI'
                )
        
        return list(result_dict.values())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"종목 검색 중 오류: {str(e)}")

@router.get("/etf/{etf_code}", response_model=StockPriceResponse)
async def get_etf_info(
    etf_code: str
):
    """ETF 정보 조회"""
    try:
        etf_data = await kis_api_client.get_etf_info(etf_code)
        
        if not etf_data:
            raise HTTPException(status_code=404, detail="ETF 정보를 찾을 수 없습니다.")
        
        return StockPriceResponse(
            stock_code=etf_code,
            stock_name=etf_data.get('prdt_name', ''),
            current_price=float(etf_data.get('stck_prpr', 0)),
            change_price=float(etf_data.get('prdy_vrss', 0)),
            change_rate=float(etf_data.get('prdy_ctrt', 0)),
            volume=int(etf_data.get('acml_vol', 0)),
            high_price=float(etf_data.get('stck_hgpr', 0)),
            low_price=float(etf_data.get('stck_lwpr', 0)),
            opening_price=float(etf_data.get('stck_oprc', 0)),
            previous_close=float(etf_data.get('stck_prpr', 0)) - float(etf_data.get('prdy_vrss', 0))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ETF 정보 조회 중 오류: {str(e)}")

@router.get("/calendar-events")
async def get_calendar_events(
    start_date: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="종료 날짜 (YYYY-MM-DD)")
):
    """캘린더 이벤트 조회 - 실제 주식 데이터 기반"""
    
    try:
        # calendar_events.json 파일에서 이벤트 로드
        import json
        import os
        
        events_file = "calendar_events.json"
        if os.path.exists(events_file):
            with open(events_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
            
            # 날짜 필터링
            if start_date and end_date:
                filtered_events = []
                for event in events:
                    event_date = event.get('start')
                    if start_date <= event_date <= end_date:
                        filtered_events.append(event)
                return filtered_events
            
            return events
        else:
            # 파일이 없으면 빈 배열 반환
            return []
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이벤트 조회 중 오류: {str(e)}")

@router.get("/overseas-stocks/{symbol}")
async def get_overseas_stock(
    symbol: str,
    market: str = Query("NAS", description="시장코드 (NAS:나스닥, NYS:뉴욕, TSE:도쿄, HKS:홍콩)")
):
    """해외 주식 현재가 조회"""
    try:
        price_data = await kis_api_client.get_overseas_stock_price(symbol, market)
        
        if not price_data:
            raise HTTPException(status_code=404, detail="해외 주식 정보를 찾을 수 없습니다.")
        
        return {
            "symbol": symbol,
            "market": market,
            "current_price": price_data.get('last', '0'),
            "change_price": price_data.get('diff', '0'),
            "change_rate": price_data.get('rate', '0'),
            "volume": price_data.get('tvol', '0'),
            "high_price": price_data.get('high', '0'),
            "low_price": price_data.get('low', '0'),
            "open_price": price_data.get('open', '0')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"해외 주식 조회 중 오류: {str(e)}")

@router.get("/cryptocurrency/{symbol}")
async def get_cryptocurrency(symbol: str = "BTC"):
    """가상화폐 시세 조회"""
    try:
        crypto_data = await kis_api_client.get_cryptocurrency_price(symbol)
        
        if not crypto_data:
            raise HTTPException(status_code=404, detail="가상화폐 정보를 찾을 수 없습니다.")
        
        return crypto_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"가상화폐 조회 중 오류: {str(e)}")

@router.get("/exchange-rate/{currency}")
async def get_exchange_rate(currency: str = "USD"):
    """환율 정보 조회"""
    try:
        exchange_data = await kis_api_client.get_exchange_rate(currency)
        
        if not exchange_data:
            raise HTTPException(status_code=404, detail="환율 정보를 찾을 수 없습니다.")
        
        return exchange_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"환율 조회 중 오류: {str(e)}")

@router.get("/disclosure/{stock_code}")
async def get_disclosure_info(stock_code: str):
    """공시 정보 조회"""
    try:
        disclosure_data = await kis_api_client.get_real_disclosure_info(stock_code)
        return disclosure_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"공시 정보 조회 중 오류: {str(e)}")

@router.get("/quotes/{stock_code}")
async def get_real_time_quotes(stock_code: str):
    """실시간 호가 정보 조회"""
    try:
        quotes_data = await kis_api_client.get_real_time_quotes(stock_code)
        
        if not quotes_data:
            raise HTTPException(status_code=404, detail="호가 정보를 찾을 수 없습니다.")
        
        return quotes_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"호가 정보 조회 중 오류: {str(e)}")

@router.get("/bonds/{bond_code}")
async def get_bond_info(bond_code: str):
    """채권 정보 조회"""
    try:
        bond_data = await kis_api_client.get_bond_info(bond_code)
        
        if not bond_data:
            raise HTTPException(status_code=404, detail="채권 정보를 찾을 수 없습니다.")
        
        return bond_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"채권 정보 조회 중 오류: {str(e)}")

@router.get("/options")
async def get_options_info():
    """선물옵션 정보 조회"""
    try:
        options_data = await kis_api_client.get_options_info()
        return options_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"선물옵션 조회 중 오류: {str(e)}")

@router.get("/top-stocks")
async def get_top_stocks():
    """인기 종목 현재가 (상위 10개) - 실제 데이터"""
    
    top_stocks = [
        {"code": "005930", "name": "삼성전자"},
        {"code": "000660", "name": "SK하이닉스"},
        {"code": "035720", "name": "카카오"},
        {"code": "051910", "name": "LG화학"},
        {"code": "006400", "name": "삼성SDI"},
        {"code": "207940", "name": "삼성바이오로직스"},
        {"code": "068270", "name": "셀트리온"},
        {"code": "066570", "name": "LG전자"},
        {"code": "005380", "name": "현대차"},
        {"code": "035420", "name": "NAVER"}
    ]
    
    try:
        results = []
        
        for stock in top_stocks:
            try:
                price_data = await kis_api_client.get_stock_price(stock["code"])
                if price_data:
                    results.append({
                        "stock_code": stock["code"],
                        "stock_name": stock["name"],
                        "current_price": price_data.get('stck_prpr', '0'),
                        "change_value": price_data.get('prdy_vrss', '0'),
                        "change_rate": price_data.get('prdy_ctrt', '0'),
                        "volume": price_data.get('acml_vol', '0')
                    })
            except:
                # 개별 종목 오류는 스킵
                continue
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"인기 종목 조회 중 오류: {str(e)}")

@router.get("/global-markets")
async def get_global_markets():
    """글로벌 시장 현황 - 실제 데이터"""
    try:
        results = {
            "us_stocks": {},
            "cryptocurrencies": {},
            "exchange_rates": {}
        }
        
        # 주요 해외 주식
        us_stocks = [
            {"symbol": "AAPL", "name": "애플"},
            {"symbol": "MSFT", "name": "마이크로소프트"},
            {"symbol": "GOOGL", "name": "구글"},
            {"symbol": "TSLA", "name": "테슬라"},
            {"symbol": "NVDA", "name": "엔비디아"}
        ]
        
        us_results = []
        for stock in us_stocks:
            try:
                data = await kis_api_client.get_overseas_stock_price(stock["symbol"], "NAS")
                if data:
                    us_results.append({
                        "symbol": stock["symbol"],
                        "name": stock["name"],
                        "price": data.get('last', '0'),
                        "change_rate": data.get('rate', '0')
                    })
            except:
                continue
        
        results["us_stocks"] = us_results
        
        # 주요 가상화폐
        crypto_symbols = ["BTC", "ETH", "XRP", "ADA", "DOT"]
        crypto_results = []
        
        for symbol in crypto_symbols:
            try:
                data = await kis_api_client.get_cryptocurrency_price(symbol)
                if data:
                    crypto_results.append({
                        "symbol": symbol,
                        "price": data.get('trade_price', 0),
                        "change_rate": data.get('change_rate', 0) * 100
                    })
            except:
                continue
        
        results["cryptocurrencies"] = crypto_results
        
        # 주요 환율
        currencies = ["USD", "EUR", "JPY", "CNY"]
        exchange_results = []
        
        for currency in currencies:
            try:
                data = await kis_api_client.get_exchange_rate(currency)
                if data:
                    exchange_results.append({
                        "currency": currency,
                        "rate": data.get('rate', 0)
                    })
            except:
                continue
        
        results["exchange_rates"] = exchange_results
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"글로벌 시장 조회 중 오류: {str(e)}")

@router.post("/ai-explain/term")
async def explain_financial_term(
    term: str = Query(..., description="설명할 금융 용어"),
    context: str = Query("", description="추가 맥락 정보")
):
    """금융 용어 AI 설명"""
    try:
        explanation = await perplexity_client.explain_financial_term(term, context)
        return explanation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"용어 설명 중 오류: {str(e)}")

@router.post("/ai-explain/event")
async def explain_market_event(
    event_title: str = Query(..., description="이벤트 제목"),
    event_details: str = Query("", description="이벤트 상세 정보")
):
    """시장 이벤트 AI 설명"""
    try:
        explanation = await perplexity_client.explain_market_event(event_title, event_details)
        return explanation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이벤트 설명 중 오류: {str(e)}")

@router.get("/ai-explain/stock/{stock_code}")
async def explain_stock_analysis(
    stock_code: str,
    stock_name: str = Query(..., description="종목명"),
    current_price: str = Query(..., description="현재가")
):
    """종목 AI 분석"""
    try:
        analysis = await perplexity_client.get_stock_analysis(stock_name, stock_code, current_price)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"종목 분석 중 오류: {str(e)}")

@router.get("/daily-market-summary")
async def get_daily_market_summary():
    """오늘의 시장 이슈 요약"""
    try:
        summary = await perplexity_client.get_daily_market_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"시장 요약 조회 중 오류: {str(e)}") 