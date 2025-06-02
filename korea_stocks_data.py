"""
한국 주식 종목 데이터
KOSPI 200 + KOSDAQ 150 주요 종목
"""

# KOSPI 주요 종목 (시가총액 상위 100개)
KOSPI_STOCKS = [
    # 대형주 (시가총액 10조 이상)
    {"code": "005930", "name": "삼성전자", "sector": "전자", "market": "KOSPI"},
    {"code": "000660", "name": "SK하이닉스", "sector": "반도체", "market": "KOSPI"},
    {"code": "005490", "name": "POSCO홀딩스", "sector": "철강", "market": "KOSPI"},
    {"code": "035420", "name": "NAVER", "sector": "인터넷", "market": "KOSPI"},
    {"code": "005380", "name": "현대차", "sector": "자동차", "market": "KOSPI"},
    {"code": "051910", "name": "LG화학", "sector": "화학", "market": "KOSPI"},
    {"code": "006400", "name": "삼성SDI", "sector": "배터리", "market": "KOSPI"},
    {"code": "035720", "name": "카카오", "sector": "인터넷", "market": "KOSPI"},
    {"code": "068270", "name": "셀트리온", "sector": "바이오", "market": "KOSPI"},
    {"code": "207940", "name": "삼성바이오로직스", "sector": "바이오", "market": "KOSPI"},
    
    # 중형주 (시가총액 1조-10조)
    {"code": "066570", "name": "LG전자", "sector": "전자", "market": "KOSPI"},
    {"code": "003670", "name": "포스코퓨처엠", "sector": "소재", "market": "KOSPI"},
    {"code": "000270", "name": "기아", "sector": "자동차", "market": "KOSPI"},
    {"code": "012330", "name": "현대모비스", "sector": "자동차부품", "market": "KOSPI"},
    {"code": "028260", "name": "삼성물산", "sector": "건설", "market": "KOSPI"},
    {"code": "105560", "name": "KB금융", "sector": "금융", "market": "KOSPI"},
    {"code": "055550", "name": "신한지주", "sector": "금융", "market": "KOSPI"},
    {"code": "086790", "name": "하나금융지주", "sector": "금융", "market": "KOSPI"},
    {"code": "096770", "name": "SK이노베이션", "sector": "화학", "market": "KOSPI"},
    {"code": "032830", "name": "삼성생명", "sector": "보험", "market": "KOSPI"},
    
    # 우량주 (대표적인 배당주, 안정성)
    {"code": "011170", "name": "롯데케미칼", "sector": "화학", "market": "KOSPI"},
    {"code": "017670", "name": "SK텔레콤", "sector": "통신", "market": "KOSPI"},
    {"code": "030200", "name": "KT", "sector": "통신", "market": "KOSPI"},
    {"code": "036570", "name": "엔씨소프트", "sector": "게임", "market": "KOSPI"},
    {"code": "034730", "name": "SK", "sector": "지주회사", "market": "KOSPI"},
    {"code": "018260", "name": "삼성에스디에스", "sector": "IT서비스", "market": "KOSPI"},
    {"code": "003550", "name": "LG", "sector": "지주회사", "market": "KOSPI"},
    {"code": "051900", "name": "LG생활건강", "sector": "화장품", "market": "KOSPI"},
    {"code": "128940", "name": "한미약품", "sector": "제약", "market": "KOSPI"},
    {"code": "009150", "name": "삼성전기", "sector": "전자부품", "market": "KOSPI"},
    
    # 성장주 (신기술, 미래산업)
    {"code": "373220", "name": "LG에너지솔루션", "sector": "배터리", "market": "KOSPI"},
    {"code": "000720", "name": "현대건설", "sector": "건설", "market": "KOSPI"},
    {"code": "010950", "name": "S-Oil", "sector": "정유", "market": "KOSPI"},
    {"code": "267250", "name": "HD현대중공업", "sector": "조선", "market": "KOSPI"},
    {"code": "042660", "name": "한화오션", "sector": "조선", "market": "KOSPI"},
    {"code": "011780", "name": "금호석유", "sector": "화학", "market": "KOSPI"},
    {"code": "005830", "name": "DB손해보험", "sector": "보험", "market": "KOSPI"},
    {"code": "138040", "name": "메리츠금융지주", "sector": "금융", "market": "KOSPI"},
    {"code": "402340", "name": "SK스퀘어", "sector": "지주회사", "market": "KOSPI"},
    {"code": "011070", "name": "LG이노텍", "sector": "전자부품", "market": "KOSPI"},
    
    # 2차전지/반도체 관련주
    {"code": "006280", "name": "녹십자", "sector": "제약", "market": "KOSPI"},
    {"code": "028050", "name": "삼성엔지니어링", "sector": "건설", "market": "KOSPI"},
    {"code": "010140", "name": "삼성중공업", "sector": "조선", "market": "KOSPI"},
    {"code": "011210", "name": "현대위아", "sector": "자동차부품", "market": "KOSPI"},
    {"code": "000810", "name": "삼성화재", "sector": "보험", "market": "KOSPI"},
    {"code": "316140", "name": "우리금융지주", "sector": "금융", "market": "KOSPI"},
    {"code": "024110", "name": "기업은행", "sector": "은행", "market": "KOSPI"},
    {"code": "001450", "name": "현대해상", "sector": "보험", "market": "KOSPI"},
    {"code": "047050", "name": "포스코인터내셔널", "sector": "상사", "market": "KOSPI"},
    {"code": "180640", "name": "한진칼", "sector": "지주회사", "market": "KOSPI"},
    
    # 소비재/유통
    {"code": "097950", "name": "CJ제일제당", "sector": "식품", "market": "KOSPI"},
    {"code": "271560", "name": "오리온", "sector": "식품", "market": "KOSPI"},
    {"code": "004020", "name": "현대제철", "sector": "철강", "market": "KOSPI"},
    {"code": "039130", "name": "하나투어", "sector": "여행", "market": "KOSPI"},
    {"code": "078930", "name": "GS", "sector": "지주회사", "market": "KOSPI"},
    {"code": "001040", "name": "CJ", "sector": "지주회사", "market": "KOSPI"},
    {"code": "079550", "name": "LIG넥스원", "sector": "방산", "market": "KOSPI"},
    {"code": "004170", "name": "신세계", "sector": "유통", "market": "KOSPI"},
    {"code": "112610", "name": "씨에스윈드", "sector": "풍력", "market": "KOSPI"},
    {"code": "000120", "name": "CJ대한통운", "sector": "물류", "market": "KOSPI"}
]

# KOSDAQ 주요 종목 (성장주 중심 50개)
KOSDAQ_STOCKS = [
    # 바이오/제약
    {"code": "196170", "name": "알테오젠", "sector": "바이오", "market": "KOSDAQ"},
    {"code": "067630", "name": "HLB생명과학", "sector": "바이오", "market": "KOSDAQ"},
    {"code": "085660", "name": "차바이오텍", "sector": "바이오", "market": "KOSDAQ"},
    {"code": "141080", "name": "레고켐바이오", "sector": "바이오", "market": "KOSDAQ"},
    {"code": "145720", "name": "덴티움", "sector": "의료기기", "market": "KOSDAQ"},
    {"code": "299030", "name": "하나제약", "sector": "제약", "market": "KOSDAQ"},
    {"code": "065510", "name": "휴젤", "sector": "바이오", "market": "KOSDAQ"},
    {"code": "214150", "name": "클래시스", "sector": "바이오", "market": "KOSDAQ"},
    {"code": "950210", "name": "프레스티지바이오파마", "sector": "바이오", "market": "KOSDAQ"},
    {"code": "195940", "name": "HK이노엔", "sector": "제약", "market": "KOSDAQ"},
    
    # IT/소프트웨어
    {"code": "039440", "name": "에스티아이", "sector": "IT", "market": "KOSDAQ"},
    {"code": "053800", "name": "안랩", "sector": "보안", "market": "KOSDAQ"},
    {"code": "060280", "name": "큐렉소", "sector": "의료진단", "market": "KOSDAQ"},
    {"code": "095340", "name": "ISC", "sector": "IT서비스", "market": "KOSDAQ"},
    {"code": "131970", "name": "두산테스나", "sector": "반도체장비", "market": "KOSDAQ"},
    {"code": "122870", "name": "와이지엔터테인먼트", "sector": "엔터", "market": "KOSDAQ"},
    {"code": "018290", "name": "브이티", "sector": "반도체", "market": "KOSDAQ"},
    {"code": "091990", "name": "셀트리온헬스케어", "sector": "바이오", "market": "KOSDAQ"},
    {"code": "058470", "name": "리노공업", "sector": "디스플레이", "market": "KOSDAQ"},
    {"code": "086900", "name": "메디톡스", "sector": "바이오", "market": "KOSDAQ"},
    
    # 2차전지/신에너지
    {"code": "121600", "name": "나노신소재", "sector": "소재", "market": "KOSDAQ"},
    {"code": "237690", "name": "에스티팜", "sector": "제약", "market": "KOSDAQ"},
    {"code": "108860", "name": "셀바스AI", "sector": "AI", "market": "KOSDAQ"},
    {"code": "036830", "name": "솔브레인", "sector": "화학", "market": "KOSDAQ"},
    {"code": "043150", "name": "바텍", "sector": "반도체장비", "market": "KOSDAQ"},
    {"code": "214420", "name": "토니모리", "sector": "화장품", "market": "KOSDAQ"},
    {"code": "096530", "name": "씨젠", "sector": "진단", "market": "KOSDAQ"},
    {"code": "112040", "name": "위메이드", "sector": "게임", "market": "KOSDAQ"},
    {"code": "039200", "name": "오스코텍", "sector": "반도체장비", "market": "KOSDAQ"},
    {"code": "064760", "name": "티씨케이", "sector": "반도체", "market": "KOSDAQ"},
    
    # 게임/엔터테인먼트
    {"code": "194480", "name": "데브시스터즈", "sector": "게임", "market": "KOSDAQ"},
    {"code": "263750", "name": "펄어비스", "sector": "게임", "market": "KOSDAQ"},
    {"code": "041510", "name": "에스엠", "sector": "엔터", "market": "KOSDAQ"},
    {"code": "035900", "name": "JYP Ent.", "sector": "엔터", "market": "KOSDAQ"},
    {"code": "376300", "name": "디어유", "sector": "화장품", "market": "KOSDAQ"},
    {"code": "950140", "name": "잉글우드랩", "sector": "게임", "market": "KOSDAQ"},
    {"code": "225570", "name": "넥슨게임즈", "sector": "게임", "market": "KOSDAQ"},
    {"code": "079160", "name": "CJ CGV", "sector": "영화", "market": "KOSDAQ"},
    {"code": "119860", "name": "커넥트웨이브", "sector": "게임", "market": "KOSDAQ"},
    {"code": "034230", "name": "파라다이스", "sector": "카지노", "market": "KOSDAQ"},
    
    # 전기차/모빌리티
    {"code": "166090", "name": "하나머티리얼즈", "sector": "반도체소재", "market": "KOSDAQ"},
    {"code": "347890", "name": "엠투아이", "sector": "모빌리티", "market": "KOSDAQ"},
    {"code": "117730", "name": "티로보틱스", "sector": "로봇", "market": "KOSDAQ"},
    {"code": "228760", "name": "지노믹트리", "sector": "진단", "market": "KOSDAQ"},
    {"code": "950130", "name": "엑세스바이오", "sector": "진단", "market": "KOSDAQ"},
    {"code": "064550", "name": "바이오니아", "sector": "바이오", "market": "KOSDAQ"},
    {"code": "256840", "name": "한국토지신탁", "sector": "부동산", "market": "KOSDAQ"},
    {"code": "054620", "name": "APS홀딩스", "sector": "반도체", "market": "KOSDAQ"},
    {"code": "083930", "name": "아바코", "sector": "IT", "market": "KOSDAQ"},
    {"code": "281740", "name": "레이크머티리얼즈", "sector": "소재", "market": "KOSDAQ"}
]

# 미국 주식 주요 종목 (확장)
US_STOCKS = [
    # 기술주 (FAANG+)
    {"symbol": "AAPL", "name": "애플", "sector": "기술", "exchange": "NASDAQ"},
    {"symbol": "MSFT", "name": "마이크로소프트", "sector": "기술", "exchange": "NASDAQ"},
    {"symbol": "GOOGL", "name": "구글(알파벳)", "sector": "기술", "exchange": "NASDAQ"},
    {"symbol": "AMZN", "name": "아마존", "sector": "전자상거래", "exchange": "NASDAQ"},
    {"symbol": "META", "name": "메타(페이스북)", "sector": "기술", "exchange": "NASDAQ"},
    {"symbol": "TSLA", "name": "테슬라", "sector": "전기차", "exchange": "NASDAQ"},
    {"symbol": "NVDA", "name": "엔비디아", "sector": "반도체", "exchange": "NASDAQ"},
    {"symbol": "NFLX", "name": "넷플릭스", "sector": "미디어", "exchange": "NASDAQ"},
    
    # AI/반도체
    {"symbol": "AMD", "name": "AMD", "sector": "반도체", "exchange": "NASDAQ"},
    {"symbol": "INTC", "name": "인텔", "sector": "반도체", "exchange": "NASDAQ"},
    {"symbol": "QCOM", "name": "퀄컴", "sector": "반도체", "exchange": "NASDAQ"},
    {"symbol": "AVGO", "name": "브로드컴", "sector": "반도체", "exchange": "NASDAQ"},
    {"symbol": "ADBE", "name": "어도비", "sector": "소프트웨어", "exchange": "NASDAQ"},
    {"symbol": "CRM", "name": "세일즈포스", "sector": "소프트웨어", "exchange": "NYSE"},
    
    # 전통 기업/금융
    {"symbol": "JPM", "name": "JP모건", "sector": "금융", "exchange": "NYSE"},
    {"symbol": "BAC", "name": "뱅크오브아메리카", "sector": "금융", "exchange": "NYSE"},
    {"symbol": "WMT", "name": "월마트", "sector": "유통", "exchange": "NYSE"},
    {"symbol": "JNJ", "name": "존슨앤존슨", "sector": "제약", "exchange": "NYSE"},
    {"symbol": "PG", "name": "P&G", "sector": "소비재", "exchange": "NYSE"},
    {"symbol": "XOM", "name": "엑손모빌", "sector": "에너지", "exchange": "NYSE"},
    
    # 성장주
    {"symbol": "UBER", "name": "우버", "sector": "모빌리티", "exchange": "NYSE"},
    {"symbol": "SHOP", "name": "쇼피파이", "sector": "전자상거래", "exchange": "NYSE"},
    {"symbol": "ZOOM", "name": "줌", "sector": "커뮤니케이션", "exchange": "NASDAQ"},
    {"symbol": "ROKU", "name": "로쿠", "sector": "미디어", "exchange": "NASDAQ"},
    {"symbol": "SQ", "name": "스퀘어(블록)", "sector": "핀테크", "exchange": "NYSE"},
    {"symbol": "PYPL", "name": "페이팔", "sector": "핀테크", "exchange": "NASDAQ"},
    
    # 바이오/제약
    {"symbol": "PFE", "name": "화이자", "sector": "제약", "exchange": "NYSE"},
    {"symbol": "MRNA", "name": "모더나", "sector": "바이오", "exchange": "NASDAQ"},
    {"symbol": "GILD", "name": "길리어드", "sector": "제약", "exchange": "NASDAQ"},
    {"symbol": "AMGN", "name": "암젠", "sector": "바이오", "exchange": "NASDAQ"}
]

def get_all_korean_stocks():
    """한국 주식 전체 목록 반환"""
    return KOSPI_STOCKS + KOSDAQ_STOCKS

def get_kospi_stocks():
    """KOSPI 종목만 반환"""
    return KOSPI_STOCKS

def get_kosdaq_stocks():
    """KOSDAQ 종목만 반환"""
    return KOSDAQ_STOCKS

def get_us_stocks():
    """미국 주식 목록 반환"""
    return US_STOCKS

def get_stocks_by_sector(sector, market=None):
    """섹터별 종목 조회"""
    all_stocks = get_all_korean_stocks()
    if market:
        all_stocks = [s for s in all_stocks if s["market"] == market]
    return [s for s in all_stocks if s["sector"] == sector]