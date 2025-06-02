from fastapi import APIRouter, Depends, HTTPException, Query, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import asyncio

from app.db.session import get_db
from app.db import models
from app.services.kis_api_refactored import kis_api_client_refactored as kis_api_client
from app.services.perplexity_api import perplexity_client
from app.services.dart_api import dart_api_client
from app.api.deps import get_current_user_optional
from app.schemas.stocks import (
    StockPriceResponse,
    StockHistoryResponse,
    MarketIndexResponse,
    InvestorTrendResponse,
    ProgramTradeResponse,
    StockSearchResponse,
    DisclosureResponse,
    CompanyInfoResponse,
    DisclosureListResponse
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
    """인기 종목 현재가 (상위 20개) - 실제 데이터"""
    
    # korea_stocks_data에서 주요 종목 가져오기
    try:
        from korea_stocks_data import KOSPI_STOCKS, KOSDAQ_STOCKS
        
        # 상위 20개 종목 선택 (KOSPI 15개 + KOSDAQ 5개)
        top_kospi = KOSPI_STOCKS[:15]
        top_kosdaq = KOSDAQ_STOCKS[:5]
        top_stocks = top_kospi + top_kosdaq
        
    except ImportError:
        # 기본 종목 리스트 (fallback)
        top_stocks = [
            {"code": "005930", "name": "삼성전자", "sector": "전자", "market": "KOSPI"},
            {"code": "000660", "name": "SK하이닉스", "sector": "반도체", "market": "KOSPI"},
            {"code": "035720", "name": "카카오", "sector": "인터넷", "market": "KOSPI"},
            {"code": "051910", "name": "LG화학", "sector": "화학", "market": "KOSPI"},
            {"code": "006400", "name": "삼성SDI", "sector": "배터리", "market": "KOSPI"},
            {"code": "207940", "name": "삼성바이오로직스", "sector": "바이오", "market": "KOSPI"},
            {"code": "068270", "name": "셀트리온", "sector": "바이오", "market": "KOSPI"},
            {"code": "066570", "name": "LG전자", "sector": "전자", "market": "KOSPI"},
            {"code": "005380", "name": "현대차", "sector": "자동차", "market": "KOSPI"},
            {"code": "035420", "name": "NAVER", "sector": "인터넷", "market": "KOSPI"},
            {"code": "373220", "name": "LG에너지솔루션", "sector": "배터리", "market": "KOSPI"},
            {"code": "012330", "name": "현대모비스", "sector": "자동차부품", "market": "KOSPI"},
            {"code": "000270", "name": "기아", "sector": "자동차", "market": "KOSPI"},
            {"code": "105560", "name": "KB금융", "sector": "금융", "market": "KOSPI"},
            {"code": "055550", "name": "신한지주", "sector": "금융", "market": "KOSPI"},
            {"code": "196170", "name": "알테오젠", "sector": "바이오", "market": "KOSDAQ"},
            {"code": "067630", "name": "HLB생명과학", "sector": "바이오", "market": "KOSDAQ"},
            {"code": "112040", "name": "위메이드", "sector": "게임", "market": "KOSDAQ"},
            {"code": "263750", "name": "펄어비스", "sector": "게임", "market": "KOSDAQ"},
            {"code": "122870", "name": "와이지엔터테인먼트", "sector": "엔터", "market": "KOSDAQ"}
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
        
        # 주요 해외 주식 (확장)
        try:
            from korea_stocks_data import US_STOCKS
            us_stocks = US_STOCKS[:12]  # 상위 12개 미국 주식
        except ImportError:
            us_stocks = [
                {"symbol": "AAPL", "name": "애플", "sector": "기술", "exchange": "NASDAQ"},
                {"symbol": "MSFT", "name": "마이크로소프트", "sector": "기술", "exchange": "NASDAQ"},
                {"symbol": "GOOGL", "name": "구글", "sector": "기술", "exchange": "NASDAQ"},
                {"symbol": "AMZN", "name": "아마존", "sector": "전자상거래", "exchange": "NASDAQ"},
                {"symbol": "TSLA", "name": "테슬라", "sector": "전기차", "exchange": "NASDAQ"},
                {"symbol": "NVDA", "name": "엔비디아", "sector": "반도체", "exchange": "NASDAQ"},
                {"symbol": "META", "name": "메타", "sector": "기술", "exchange": "NASDAQ"},
                {"symbol": "NFLX", "name": "넷플릭스", "sector": "미디어", "exchange": "NASDAQ"},
                {"symbol": "AMD", "name": "AMD", "sector": "반도체", "exchange": "NASDAQ"},
                {"symbol": "INTC", "name": "인텔", "sector": "반도체", "exchange": "NASDAQ"},
                {"symbol": "JPM", "name": "JP모건", "sector": "금융", "exchange": "NYSE"},
                {"symbol": "BAC", "name": "뱅크오브아메리카", "sector": "금융", "exchange": "NYSE"}
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
    term: str = Form(..., description="설명할 금융 용어"),
    context: str = Form("", description="추가 맥락 정보")
):
    """금융 용어 AI 설명"""
    try:
        explanation = await perplexity_client.explain_financial_term(term, context)
        return explanation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"용어 설명 중 오류: {str(e)}")

@router.post("/ai-explain/event")
async def explain_market_event(
    event_title: str = Form(..., description="이벤트 제목"),
    event_details: str = Form("", description="이벤트 상세 정보")
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

# ==================== DART API 엔드포인트 ====================

@router.get("/disclosures", response_model=DisclosureListResponse)
async def get_disclosures(
    corp_code: str = Query(None, description="고유번호(8자리)"),
    corp_cls: str = Query("Y", description="법인구분 (Y:유가, K:코스닥, N:코넥스, E:기타)"),
    days: int = Query(7, description="조회 기간(일)", ge=1, le=30),
    page_no: int = Query(1, description="페이지 번호", ge=1),
    page_count: int = Query(10, description="페이지당 건수", ge=1, le=100)
):
    """공시정보 조회"""
    try:
        from datetime import datetime, timedelta
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        result = await dart_api_client.get_disclosure_list(
            corp_code=corp_code,
            bgn_de=start_date.strftime("%Y%m%d"),
            end_de=end_date.strftime("%Y%m%d"),
            corp_cls=corp_cls,
            page_no=page_no,
            page_count=page_count
        )
        
        if result["success"]:
            return DisclosureListResponse(
                success=True,
                data=[DisclosureResponse(**item) for item in result["data"]],
                page_info=result.get("page_info")
            )
        else:
            return DisclosureListResponse(
                success=False,
                error=result.get("error", "공시정보 조회 실패")
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"공시정보 조회 중 오류: {str(e)}")

@router.get("/company/{corp_code}", response_model=CompanyInfoResponse)
async def get_company_info(corp_code: str):
    """기업개황 조회"""
    try:
        result = await dart_api_client.get_company_info(corp_code)
        
        if result["success"]:
            return CompanyInfoResponse(**result["data"])
        else:
            raise HTTPException(
                status_code=404, 
                detail=result.get("error", "기업 정보를 찾을 수 없습니다.")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"기업개황 조회 중 오류: {str(e)}")

@router.get("/recent-disclosures")
async def get_recent_disclosures(
    corp_cls: str = Query("Y", description="법인구분 (Y:유가, K:코스닥)"),
    days: int = Query(7, description="조회 기간(일)", ge=1, le=30),
    important_only: bool = Query(True, description="중요 공시만 조회")
):
    """최근 중요 공시 조회 (캘린더 이벤트용)"""
    try:
        disclosures = await dart_api_client.get_recent_disclosures(
            corp_cls=corp_cls,
            days=days,
            important_only=important_only
        )
        
        return {
            "success": True,
            "count": len(disclosures),
            "data": disclosures
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"최근 공시 조회 중 오류: {str(e)}")

@router.get("/search-company")
async def search_company(
    company_name: str = Query(..., description="회사명 (부분 검색 가능)")
):
    """회사명으로 기업 검색"""
    try:
        companies = await dart_api_client.search_company_by_name(company_name)
        
        return {
            "success": True,
            "count": len(companies),
            "data": companies
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"기업 검색 중 오류: {str(e)}")

@router.get("/disclosure/{rcept_no}")
async def get_disclosure_detail(rcept_no: str):
    """공시 상세 조회 (DART 뷰어 링크 제공)"""
    try:
        # DART 공시뷰어 링크 생성
        dart_viewer_url = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}"
        
        return {
            "success": True,
            "rcept_no": rcept_no,
            "dart_viewer_url": dart_viewer_url,
            "message": "공시 상세 내용은 DART 뷰어에서 확인할 수 있습니다."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"공시 상세 조회 중 오류: {str(e)}")

@router.get("/market-indices")
async def get_market_indices():
    """한국 시장 지수 조회 (KOSPI, KOSDAQ, KRX100 등)"""
    try:
        indices = {}
        
        # 주요 지수 코드
        index_codes = {
            "KOSPI": "0001",      # 코스피 지수
            "KOSDAQ": "1001",     # 코스닥 지수  
            "KRX100": "2203",     # KRX100 지수
            "KOSPI200": "1028"    # 코스피200 지수
        }
        
        for index_name, index_code in index_codes.items():
            try:
                index_data = await kis_api_client.get_market_index(index_code)
                if index_data:
                    indices[index_name] = {
                        "name": index_name,
                        "code": index_code,
                        "current_value": index_data.get('bstp_nmix_prpr', 0),
                        "change_value": index_data.get('bstp_nmix_prdy_vrss', 0),
                        "change_rate": index_data.get('prdy_vrss_sign', 0),
                        "volume": index_data.get('acml_vol', 0),
                        "market_cap": index_data.get('bstp_nmix_total_askp', 0)
                    }
            except Exception as e:
                print(f"{index_name} 지수 조회 실패: {e}")
                # 기본 값 설정 (API 실패 시)
                indices[index_name] = {
                    "name": index_name,
                    "code": index_code,
                    "current_value": 0,
                    "change_value": 0,
                    "change_rate": 0,
                    "volume": 0,
                    "market_cap": 0,
                    "error": "데이터 로딩 실패"
                }
        
        return {
            "success": True,
            "indices": indices,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"시장 지수 조회 중 오류: {str(e)}")

@router.get("/sectors")
async def get_sector_performance():
    """섹터별 성과 조회"""
    try:
        from korea_stocks_data import get_stocks_by_sector
        
        sectors = ["전자", "반도체", "자동차", "화학", "바이오", "금융", "게임", "인터넷"]
        sector_performance = {}
        
        for sector in sectors:
            sector_stocks = get_stocks_by_sector(sector)[:5]  # 각 섹터 상위 5개
            sector_data = []
            
            for stock in sector_stocks:
                try:
                    price_data = await kis_api_client.get_stock_price(stock["code"])
                    if price_data:
                        sector_data.append({
                            "code": stock["code"],
                            "name": stock["name"],
                            "market": stock["market"],
                            "current_price": price_data.get('stck_prpr', '0'),
                            "change_rate": price_data.get('prdy_ctrt', '0')
                        })
                except:
                    continue
            
            if sector_data:
                # 섹터 평균 수익률 계산
                avg_change = sum(float(s.get('change_rate', 0)) for s in sector_data) / len(sector_data)
                sector_performance[sector] = {
                    "stocks": sector_data,
                    "avg_change_rate": round(avg_change, 2),
                    "stock_count": len(sector_data)
                }
        
        return {
            "success": True,
            "sectors": sector_performance,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"섹터 성과 조회 중 오류: {str(e)}")

@router.get("/korean-stocks/all")
async def get_all_korean_stocks():
    """전체 한국 주식 목록 조회"""
    try:
        from korea_stocks_data import get_all_korean_stocks
        all_stocks = get_all_korean_stocks()
        
        return {
            "success": True,
            "total_count": len(all_stocks),
            "kospi_count": len([s for s in all_stocks if s["market"] == "KOSPI"]),
            "kosdaq_count": len([s for s in all_stocks if s["market"] == "KOSDAQ"]),
            "stocks": all_stocks,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"전체 주식 목록 조회 중 오류: {str(e)}")

@router.get("/calendar/all-events")
async def get_all_calendar_events(
    start_date: str = Query(..., description="시작 날짜 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="종료 날짜 (YYYY-MM-DD)")
):
    """포괄적인 캘린더 이벤트 조회 (기본 이벤트 + 실시간 공시 + 실시간 데이터)"""
    try:
        all_events = []
        
        # 1. 기본 캘린더 이벤트 로드
        try:
            import os
            import json
            
            # 프로젝트 루트 디렉토리에서 파일 찾기
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
            calendar_file_path = os.path.join(project_root, 'calendar_events.json')
            
            # 파일이 없으면 현재 작업 디렉토리에서 찾기
            if not os.path.exists(calendar_file_path):
                calendar_file_path = 'calendar_events.json'
            
            # 절대 경로로 재시도
            if not os.path.exists(calendar_file_path):
                calendar_file_path = '/Users/yeong-gwang/Desktop/work/서울경제신문/경제용/미팅/주식캘린더/calendar_events.json'
            
            if os.path.exists(calendar_file_path):
                with open(calendar_file_path, 'r', encoding='utf-8') as f:
                    basic_events = json.load(f)
                    all_events.extend(basic_events)
                    print(f"✅ 기본 캘린더 이벤트 {len(basic_events)}개 로드 완료")
            else:
                print("⚠️ 캘린더 이벤트 파일을 찾을 수 없습니다.")
                
        except Exception as e:
            print(f"⚠️ 캘린더 이벤트 로드 중 오류: {e}")
        
        # 2. 실시간 DART 공시정보 추가
        try:
            recent_disclosures = await dart_api_client.get_recent_disclosures(
                corp_cls="Y",  # 유가증권
                days=30,
                important_only=True
            )
            
            for disclosure in recent_disclosures[:10]:  # 최근 10개만
                try:
                    # 접수일을 날짜로 변환
                    rcept_dt = disclosure.get('rcept_dt', '')
                    if len(rcept_dt) == 8:  # YYYYMMDD 형식
                        event_date = f"{rcept_dt[:4]}-{rcept_dt[4:6]}-{rcept_dt[6:8]}"
                        
                        all_events.append({
                            "id": f"disclosure_{disclosure.get('rcept_no')}",
                            "title": f"📄 {disclosure.get('corp_name')} 공시",
                            "start": event_date,
                            "backgroundColor": "#3b82f6",
                            "borderColor": "#3b82f6",
                            "extendedProps": {
                                "eventType": "disclosure",
                                "stockCode": disclosure.get('stock_code'),
                                "stockName": disclosure.get('corp_name'),
                                "description": f"{disclosure.get('corp_name')} {disclosure.get('report_nm')}",
                                "importance": "medium",
                                "details": f"보고서: {disclosure.get('report_nm')}\\n제출인: {disclosure.get('flr_nm')}\\n접수번호: {disclosure.get('rcept_no')}",
                                "rcept_no": disclosure.get('rcept_no'),
                                "report_nm": disclosure.get('report_nm')
                            }
                        })
                except Exception as e:
                    print(f"공시 이벤트 변환 실패: {e}")
                    continue
                    
        except Exception as e:
            print(f"DART 공시정보 조회 실패: {e}")
        
        # 3. 주요 종목 실시간 데이터로 이벤트 업데이트
        try:
            from korea_stocks_data import KOSPI_STOCKS
            major_stocks = KOSPI_STOCKS[:5]  # 상위 5개 종목
            
            for stock in major_stocks:
                try:
                    price_data = await kis_api_client.get_stock_price(stock["code"])
                    if price_data:
                        current_price = price_data.get('stck_prpr', '0')
                        change_rate = float(price_data.get('prdy_ctrt', '0'))
                        
                        # 주가 변동이 큰 경우 이벤트 추가 (5% 이상)
                        if abs(change_rate) >= 5.0:
                            today = datetime.now().strftime("%Y-%m-%d")
                            all_events.append({
                                "id": f"price_alert_{stock['code']}",
                                "title": f"🚨 {stock['name']} 급등락 ({change_rate:+.1f}%)",
                                "start": today,
                                "backgroundColor": "#dc2626" if change_rate < 0 else "#16a34a",
                                "borderColor": "#dc2626" if change_rate < 0 else "#16a34a",
                                "extendedProps": {
                                    "eventType": "price_alert",
                                    "stockCode": stock["code"],
                                    "stockName": stock["name"],
                                    "description": f"{stock['name']} 주가가 {change_rate:+.1f}% 변동했습니다.",
                                    "importance": "high",
                                    "details": f"현재가: {current_price}원\\n변동률: {change_rate:+.1f}%\\n시장: {stock['market']}",
                                    "currentPrice": current_price,
                                    "changeRate": change_rate
                                }
                            })
                except Exception as e:
                    print(f"주가 데이터 조회 실패 ({stock['code']}): {e}")
                    continue
                    
        except Exception as e:
            print(f"실시간 주가 데이터 조회 실패: {e}")
        
        # 4. 날짜 필터링
        filtered_events = []
        for event in all_events:
            event_date = event.get('start', '')
            if start_date <= event_date <= end_date:
                filtered_events.append(event)
        
        # 5. 날짜순 정렬
        filtered_events.sort(key=lambda x: x.get('start', ''))
        
        return {
            "success": True,
            "total_events": len(filtered_events),
            "events": filtered_events,
            "event_types": {
                "earnings": len([e for e in filtered_events if e.get('extendedProps', {}).get('eventType') == 'earnings']),
                "dividend": len([e for e in filtered_events if e.get('extendedProps', {}).get('eventType') == 'dividend']),
                "economic": len([e for e in filtered_events if e.get('extendedProps', {}).get('eventType') == 'economic']),
                "disclosure": len([e for e in filtered_events if e.get('extendedProps', {}).get('eventType') == 'disclosure']),
                "crypto": len([e for e in filtered_events if e.get('extendedProps', {}).get('eventType') == 'crypto']),
                "holiday": len([e for e in filtered_events if e.get('extendedProps', {}).get('eventType') == 'holiday']),
                "price_alert": len([e for e in filtered_events if e.get('extendedProps', {}).get('eventType') == 'price_alert'])
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"캘린더 이벤트 조회 중 오류: {str(e)}") 