"""
DART(전자공시시스템) API 클라이언트
공시정보 및 기업개황 조회 서비스
"""
import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class DARTAPIClient:
    """DART(전자공시시스템) Open API 클라이언트"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.DART_API_KEY
        self.base_url = "https://opendart.fss.or.kr/api"
        
    async def get_disclosure_list(
        self,
        corp_code: str = None,
        bgn_de: str = None,
        end_de: str = None,
        corp_cls: str = None,
        page_no: int = 1,
        page_count: int = 10
    ) -> Dict[str, Any]:
        """
        공시검색 - 공시정보를 조회합니다
        
        Args:
            corp_code: 고유번호(8자리) - 특정 회사의 공시만 조회
            bgn_de: 시작일(YYYYMMDD)
            end_de: 종료일(YYYYMMDD) 
            corp_cls: 법인구분 (Y:유가, K:코스닥, N:코넥스, E:기타)
            page_no: 페이지 번호
            page_count: 페이지당 건수(최대 100)
        """
        try:
            # 기본값 설정: 최근 7일간 공시
            if not end_de:
                end_de = datetime.now().strftime("%Y%m%d")
            if not bgn_de:
                bgn_de = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")
                
            params = {
                "crtfc_key": self.api_key,
                "page_no": page_no,
                "page_count": min(page_count, 100)  # 최대 100건
            }
            
            # 선택적 파라미터 추가
            if corp_code:
                params["corp_code"] = corp_code
            if bgn_de:
                params["bgn_de"] = bgn_de
            if end_de:
                params["end_de"] = end_de
            if corp_cls:
                params["corp_cls"] = corp_cls
                
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/list.json",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == "000":
                            return {
                                "success": True,
                                "data": data.get("list", []),
                                "page_info": {
                                    "page_no": data.get("page_no"),
                                    "page_count": data.get("page_count"),
                                    "total_count": data.get("total_count"),
                                    "total_page": data.get("total_page")
                                }
                            }
                        else:
                            logger.error(f"DART API 오류: {data.get('message')}")
                            return {"success": False, "error": data.get("message")}
                    else:
                        logger.error(f"DART API HTTP 오류: {response.status}")
                        return {"success": False, "error": f"HTTP {response.status}"}
                        
        except Exception as e:
            logger.error(f"DART API 공시검색 실패: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_company_info(self, corp_code: str) -> Dict[str, Any]:
        """
        기업개황 조회
        
        Args:
            corp_code: 고유번호(8자리)
        """
        try:
            params = {
                "crtfc_key": self.api_key,
                "corp_code": corp_code
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/company.json",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == "000":
                            return {
                                "success": True,
                                "data": {
                                    "corp_name": data.get("corp_name"),
                                    "corp_name_eng": data.get("corp_name_eng"),
                                    "stock_name": data.get("stock_name"),
                                    "stock_code": data.get("stock_code"),
                                    "ceo_nm": data.get("ceo_nm"),
                                    "corp_cls": data.get("corp_cls"),
                                    "adres": data.get("adres"),
                                    "hm_url": data.get("hm_url"),
                                    "ir_url": data.get("ir_url"),
                                    "phn_no": data.get("phn_no"),
                                    "induty_code": data.get("induty_code"),
                                    "est_dt": data.get("est_dt"),
                                    "acc_mt": data.get("acc_mt")
                                }
                            }
                        else:
                            logger.error(f"DART API 기업개황 오류: {data.get('message')}")
                            return {"success": False, "error": data.get("message")}
                    else:
                        logger.error(f"DART API HTTP 오류: {response.status}")
                        return {"success": False, "error": f"HTTP {response.status}"}
                        
        except Exception as e:
            logger.error(f"DART API 기업개황 조회 실패: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_recent_disclosures(
        self, 
        corp_cls: str = "Y", 
        days: int = 7,
        important_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        최근 중요 공시 조회 (캘린더 이벤트용)
        
        Args:
            corp_cls: 법인구분 (Y:유가, K:코스닥)
            days: 조회 기간 (일)
            important_only: 중요 공시만 필터링
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            result = await self.get_disclosure_list(
                bgn_de=start_date.strftime("%Y%m%d"),
                end_de=end_date.strftime("%Y%m%d"),
                corp_cls=corp_cls,
                page_count=100
            )
            
            if not result["success"]:
                return []
            
            disclosures = result["data"]
            
            # 중요 공시 키워드 필터링
            if important_only:
                important_keywords = [
                    "실적발표", "실적공시", "분기보고서", "반기보고서", "사업보고서",
                    "임시주주총회", "정기주주총회", "배당", "유상증자", "무상증자",
                    "합병", "분할", "인수", "매각", "대규모내부거래",
                    "주요사항보고", "공시정정", "특별관계자거래"
                ]
                
                filtered_disclosures = []
                for disclosure in disclosures:
                    report_name = disclosure.get("report_nm", "")
                    if any(keyword in report_name for keyword in important_keywords):
                        filtered_disclosures.append(disclosure)
                
                return filtered_disclosures[:20]  # 최대 20건
            
            return disclosures[:20]
            
        except Exception as e:
            logger.error(f"최근 공시 조회 실패: {e}")
            return []
    
    async def search_company_by_name(self, company_name: str) -> List[Dict[str, Any]]:
        """
        회사명으로 기업 검색 (부분 검색)
        """
        try:
            # 최근 30일 공시에서 회사명 검색
            result = await self.get_disclosure_list(
                bgn_de=(datetime.now() - timedelta(days=30)).strftime("%Y%m%d"),
                page_count=100
            )
            
            if not result["success"]:
                return []
            
            # 회사명으로 필터링
            companies = {}
            for disclosure in result["data"]:
                corp_name = disclosure.get("corp_name", "")
                if company_name.lower() in corp_name.lower():
                    corp_code = disclosure.get("corp_code")
                    if corp_code and corp_code not in companies:
                        companies[corp_code] = {
                            "corp_code": corp_code,
                            "corp_name": corp_name,
                            "stock_code": disclosure.get("stock_code"),
                            "corp_cls": disclosure.get("corp_cls")
                        }
            
            return list(companies.values())[:10]  # 최대 10건
            
        except Exception as e:
            logger.error(f"회사 검색 실패: {e}")
            return []

# 전역 DART API 클라이언트 인스턴스
dart_api_client = DARTAPIClient()