"""
캘린더 이벤트 생성 스크립트
=========================
이 스크립트는 투자 캘린더를 위한 이벤트 데이터를 생성하고 calendar_events.json 파일로 저장합니다.
주식, 경제지표, 가상화폐, 글로벌 이벤트 등 다양한 투자 관련 이벤트를 포함합니다.

실행 방법:
python calendar_generator.py

출력:
- calendar_events.json: 캘린더 이벤트 데이터 파일
"""
from datetime import datetime, timedelta, date
import json

def generate_extended_events():
    """2025년 전체 연도 투자 캘린더 이벤트 생성
    
    실적발표, 배당, 경제지표, 가상화폐, 휴장일 등 모든 투자 관련 이벤트를 생성합니다.
    이벤트는 fullcalendar 형식으로 생성됩니다.
    
    Returns:
        list: 투자 캘린더 이벤트 목록
    """
    
    events = []
    
    # 2025년 기준 날짜들
    year_2025 = 2025
    
    # =========================== 한국 증시 이벤트 ===========================
    
    # 주요 기업 실적발표 (분기별 - 2025년 전체)
    korean_earnings = [
        # 1분기 실적 (4월)
        {"company": "삼성전자", "code": "005930", "quarter": "1Q25", "date": "2025-04-25"},
        {"company": "SK하이닉스", "code": "000660", "quarter": "1Q25", "date": "2025-04-28"},
        {"company": "NAVER", "code": "035420", "quarter": "1Q25", "date": "2025-04-30"},
        {"company": "카카오", "code": "035720", "quarter": "1Q25", "date": "2025-05-02"},
        {"company": "LG화학", "code": "051910", "quarter": "1Q25", "date": "2025-05-05"},
        {"company": "현대차", "code": "005380", "quarter": "1Q25", "date": "2025-05-07"},
        {"company": "셀트리온", "code": "068270", "quarter": "1Q25", "date": "2025-05-09"},
        
        # 2분기 실적 (7월)
        {"company": "삼성전자", "code": "005930", "quarter": "2Q25", "date": "2025-07-25"},
        {"company": "SK하이닉스", "code": "000660", "quarter": "2Q25", "date": "2025-07-28"},
        {"company": "NAVER", "code": "035420", "quarter": "2Q25", "date": "2025-07-30"},
        {"company": "카카오", "code": "035720", "quarter": "2Q25", "date": "2025-08-01"},
        {"company": "LG화학", "code": "051910", "quarter": "2Q25", "date": "2025-08-04"},
        
        # 3분기 실적 (10월)
        {"company": "삼성전자", "code": "005930", "quarter": "3Q25", "date": "2025-10-24"},
        {"company": "SK하이닉스", "code": "000660", "quarter": "3Q25", "date": "2025-10-27"},
        {"company": "NAVER", "code": "035420", "quarter": "3Q25", "date": "2025-10-29"},
        {"company": "카카오", "code": "035720", "quarter": "3Q25", "date": "2025-10-31"},
        
        # 4분기 실적 (1월 - 작년 실적)
        {"company": "삼성전자", "code": "005930", "quarter": "4Q24", "date": "2025-01-24"},
        {"company": "SK하이닉스", "code": "000660", "quarter": "4Q24", "date": "2025-01-27"},
        {"company": "NAVER", "code": "035420", "quarter": "4Q24", "date": "2025-01-29"},
        {"company": "카카오", "code": "035720", "quarter": "4Q24", "date": "2025-01-31"},
    ]
    
    for earning in korean_earnings:
        events.append({
            "id": f"earning_{earning['code']}_{earning['quarter']}",
            "title": f"📊 {earning['company']} {earning['quarter']} 실적발표",
            "start": earning["date"],
            "backgroundColor": "#10b981",
            "borderColor": "#10b981",
            "extendedProps": {
                "eventType": "earnings",
                "stockCode": earning["code"],
                "stockName": earning["company"],
                "description": f"{earning['company']} {earning['quarter']} 실적발표입니다. 매출액, 영업이익, 순이익 등 주요 재무지표가 공개됩니다.",
                "importance": "high",
                "details": f"시간: 16:00 (장마감 후)\\n장소: 실적설명회\\n예상: 시장 관심도 높음",
                "time": "16:00"
            }
        })
    
    # 국내 주요 기업 배당 일정 (2025년)
    korean_dividends = [
        {"company": "삼성전자", "code": "005930", "type": "결산배당", "date": "2025-04-15", "amount": "1,500원"},
        {"company": "SK하이닉스", "code": "000660", "type": "결산배당", "date": "2025-04-18", "amount": "1,200원"},
        {"company": "NAVER", "code": "035420", "type": "중간배당", "date": "2025-09-15", "amount": "600원"},
        {"company": "현대차", "code": "005380", "type": "결산배당", "date": "2025-05-20", "amount": "2,800원"},
        {"company": "KB금융", "code": "105560", "type": "분기배당", "date": "2025-03-15", "amount": "450원"},
        {"company": "신한지주", "code": "055550", "type": "분기배당", "date": "2025-06-15", "amount": "400원"},
        {"company": "LG화학", "code": "051910", "type": "결산배당", "date": "2025-05-25", "amount": "800원"},
        {"company": "POSCO홀딩스", "code": "005490", "type": "결산배당", "date": "2025-04-20", "amount": "2,000원"},
    ]
    
    for dividend in korean_dividends:
        events.append({
            "id": f"dividend_{dividend['code']}_{dividend['date']}",
            "title": f"💰 {dividend['company']} 배당금 지급",
            "start": dividend["date"],
            "backgroundColor": "#f59e0b",
            "borderColor": "#f59e0b",
            "extendedProps": {
                "eventType": "dividend",
                "stockCode": dividend["code"],
                "stockName": dividend["company"],
                "description": f"{dividend['company']} {dividend['type']} 배당금 {dividend['amount']} 지급일입니다.",
                "importance": "medium",
                "details": f"배당금: {dividend['amount']}\\n배당유형: {dividend['type']}\\n권리락일: 배당지급일 2영업일 전",
                "amount": dividend["amount"]
            }
        })
    
    # =========================== 미국 증시 이벤트 ===========================
    
    # 미국 주요 기업 실적발표 (2025년)
    us_earnings = [
        # 1분기 (4-5월)
        {"company": "Apple", "symbol": "AAPL", "quarter": "Q1 2025", "date": "2025-05-01"},
        {"company": "Microsoft", "symbol": "MSFT", "quarter": "Q1 2025", "date": "2025-04-26"},
        {"company": "Google", "symbol": "GOOGL", "quarter": "Q1 2025", "date": "2025-04-29"},
        {"company": "Amazon", "symbol": "AMZN", "quarter": "Q1 2025", "date": "2025-05-03"},
        {"company": "Tesla", "symbol": "TSLA", "quarter": "Q1 2025", "date": "2025-04-24"},
        {"company": "NVIDIA", "symbol": "NVDA", "quarter": "Q1 2025", "date": "2025-05-21"},
        
        # 2분기 (7-8월)
        {"company": "Apple", "symbol": "AAPL", "quarter": "Q2 2025", "date": "2025-08-01"},
        {"company": "Microsoft", "symbol": "MSFT", "quarter": "Q2 2025", "date": "2025-07-26"},
        {"company": "Google", "symbol": "GOOGL", "quarter": "Q2 2025", "date": "2025-07-29"},
        {"company": "Amazon", "symbol": "AMZN", "quarter": "Q2 2025", "date": "2025-08-03"},
        
        # 3분기 (10-11월)
        {"company": "Apple", "symbol": "AAPL", "quarter": "Q3 2025", "date": "2025-11-01"},
        {"company": "Microsoft", "symbol": "MSFT", "quarter": "Q3 2025", "date": "2025-10-26"},
        
        # 4분기 2024 (1-2월)
        {"company": "Apple", "symbol": "AAPL", "quarter": "Q4 2024", "date": "2025-02-01"},
        {"company": "Microsoft", "symbol": "MSFT", "quarter": "Q4 2024", "date": "2025-01-26"},
    ]
    
    for earning in us_earnings:
        events.append({
            "id": f"us_earning_{earning['symbol']}_{earning['quarter'].replace(' ', '_')}",
            "title": f"🇺🇸 {earning['company']} 실적발표",
            "start": earning["date"],
            "backgroundColor": "#3b82f6",
            "borderColor": "#3b82f6",
            "extendedProps": {
                "eventType": "earnings",
                "stockCode": earning["symbol"],
                "stockName": earning["company"],
                "description": f"{earning['company']} {earning['quarter']} 실적발표입니다. 매출, EPS 등 주요 지표가 발표됩니다.",
                "importance": "high",
                "details": f"시간: 장마감 후 (한국시간 06:00)\\n시장: 미국 증시\\n예상: 글로벌 시장 영향",
                "market": "US",
                "time": "06:00 (한국시간)"
            }
        })
    
    # =========================== 경제지표 및 정책 이벤트 ===========================
    
    # 미국 경제지표 (2025년)
    us_economic_events = [
        {"event": "FOMC 회의", "date": "2025-01-29", "impact": "very_high"},
        {"event": "미국 CPI 발표", "date": "2025-02-12", "impact": "high"},
        {"event": "FOMC 회의", "date": "2025-03-19", "impact": "very_high"},
        {"event": "미국 고용지표", "date": "2025-04-04", "impact": "high"},
        {"event": "FOMC 회의", "date": "2025-05-01", "impact": "very_high"},
        {"event": "미국 GDP 발표", "date": "2025-05-29", "impact": "high"},
        {"event": "FOMC 회의", "date": "2025-06-18", "impact": "very_high"},
        {"event": "미국 CPI 발표", "date": "2025-07-10", "impact": "high"},
        {"event": "FOMC 회의", "date": "2025-07-30", "impact": "very_high"},
        {"event": "FOMC 회의", "date": "2025-09-17", "impact": "very_high"},
        {"event": "미국 고용지표", "date": "2025-10-03", "impact": "high"},
        {"event": "FOMC 회의", "date": "2025-11-05", "impact": "very_high"},
        {"event": "FOMC 회의", "date": "2025-12-17", "impact": "very_high"},
    ]
    
    for event_info in us_economic_events:
        events.append({
            "id": f"us_economic_{event_info['date']}",
            "title": f"🏛️ {event_info['event']}",
            "start": event_info["date"],
            "backgroundColor": "#dc2626",
            "borderColor": "#dc2626",
            "extendedProps": {
                "eventType": "economic",
                "description": f"미국 {event_info['event']}입니다. 글로벌 금융시장에 큰 영향을 미칠 수 있습니다.",
                "importance": event_info["impact"],
                "details": f"시간: 22:30 (한국시간)\\n발표기관: 미국 연방준비제도\\n영향도: {event_info['impact']}",
                "market": "Global",
                "time": "22:30 (한국시간)"
            }
        })
    
    # 한국 경제지표 (2025년)
    korean_economic_events = [
        {"event": "한국은행 기준금리 결정", "date": "2025-01-16", "impact": "very_high"},
        {"event": "한국 GDP 발표", "date": "2025-01-25", "impact": "high"},
        {"event": "한국은행 기준금리 결정", "date": "2025-02-13", "impact": "very_high"},
        {"event": "한국 CPI 발표", "date": "2025-03-05", "impact": "high"},
        {"event": "한국은행 기준금리 결정", "date": "2025-04-10", "impact": "very_high"},
        {"event": "한국 고용동향", "date": "2025-05-14", "impact": "medium"},
        {"event": "한국은행 기준금리 결정", "date": "2025-05-29", "impact": "very_high"},
        {"event": "한국 무역수지", "date": "2025-06-01", "impact": "medium"},
        {"event": "한국은행 기준금리 결정", "date": "2025-07-11", "impact": "very_high"},
        {"event": "한국 GDP 발표", "date": "2025-07-25", "impact": "high"},
        {"event": "한국은행 기준금리 결정", "date": "2025-08-28", "impact": "very_high"},
        {"event": "한국 CPI 발표", "date": "2025-09-03", "impact": "high"},
        {"event": "한국은행 기준금리 결정", "date": "2025-10-16", "impact": "very_high"},
        {"event": "한국은행 기준금리 결정", "date": "2025-11-27", "impact": "very_high"},
    ]
    
    for event_info in korean_economic_events:
        events.append({
            "id": f"kr_economic_{event_info['date']}",
            "title": f"🇰🇷 {event_info['event']}",
            "start": event_info["date"],
            "backgroundColor": "#14b8a6",
            "borderColor": "#14b8a6",
            "extendedProps": {
                "eventType": "economic",
                "description": f"한국 주요 경제지표: {event_info['event']}",
                "importance": event_info["impact"],
                "details": f"시간: 08:00\\n발표기관: 한국은행/통계청\\n영향도: {event_info['impact']}",
                "market": "Korea",
                "time": "08:00"
            }
        })
    
    # =========================== 가상화폐 이벤트 ===========================
    
    crypto_events = [
        {"event": "비트코인 ETF 승인 1주년", "date": "2025-01-11", "impact": "high"},
        {"event": "이더리움 상하이 업그레이드 2주년", "date": "2025-03-12", "impact": "medium"},
        {"event": "비트코인 반감기 1주년", "date": "2025-04-20", "impact": "very_high"},
        {"event": "솔라나 생태계 컨퍼런스", "date": "2025-06-15", "impact": "medium"},
        {"event": "리플 SEC 소송 결과 예상", "date": "2025-07-30", "impact": "high"},
        {"event": "이더리움 2.0 완전 전환 3주년", "date": "2025-09-15", "impact": "medium"},
        {"event": "도지코인 창립 12주년", "date": "2025-12-06", "impact": "low"},
        {"event": "암호화폐 시장 연말 결산", "date": "2025-12-31", "impact": "medium"},
    ]
    
    for crypto in crypto_events:
        events.append({
            "id": f"crypto_{crypto['date']}",
            "title": f"₿ {crypto['event']}",
            "start": crypto["date"],
            "backgroundColor": "#f97316",
            "borderColor": "#f97316",
            "extendedProps": {
                "eventType": "crypto",
                "description": f"가상화폐 시장 주요 이벤트: {crypto['event']}",
                "importance": crypto["impact"],
                "details": f"영향도: {crypto['impact']}\\n시장: 글로벌 가상화폐\\n관련 코인: BTC, ETH 등",
                "market": "Crypto"
            }
        })
    
    # =========================== 한국 공휴일 및 시장 휴장일 ===========================
    
    holidays = [
        {"event": "신정", "date": "2025-01-01", "type": "holiday"},
        {"event": "설날", "date": "2025-01-28", "type": "holiday"},
        {"event": "설날 연휴", "date": "2025-01-29", "type": "holiday"},
        {"event": "설날 연휴", "date": "2025-01-30", "type": "holiday"},
        {"event": "삼일절", "date": "2025-03-01", "type": "holiday"},
        {"event": "어린이날", "date": "2025-05-05", "type": "holiday"},
        {"event": "부처님오신날", "date": "2025-05-05", "type": "holiday"},
        {"event": "현충일", "date": "2025-06-06", "type": "holiday"},
        {"event": "광복절", "date": "2025-08-15", "type": "holiday"},
        {"event": "추석", "date": "2025-10-06", "type": "holiday"},
        {"event": "추석 연휴", "date": "2025-10-07", "type": "holiday"},
        {"event": "추석 연휴", "date": "2025-10-08", "type": "holiday"},
        {"event": "개천절", "date": "2025-10-03", "type": "holiday"},
        {"event": "한글날", "date": "2025-10-09", "type": "holiday"},
        {"event": "성탄절", "date": "2025-12-25", "type": "holiday"},
    ]
    
    for holiday in holidays:
        events.append({
            "id": f"holiday_{holiday['date']}",
            "title": f"🏛️ {holiday['event']}",
            "start": holiday["date"],
            "backgroundColor": "#6b7280",
            "borderColor": "#6b7280",
            "extendedProps": {
                "eventType": "holiday",
                "description": f"한국 공휴일: {holiday['event']} (증시 휴장)",
                "importance": "low",
                "details": f"한국 증시 휴장일\\n해외 증시는 정상 거래",
                "market": "Korea"
            }
        })
    
    # =========================== 주요 글로벌 이벤트 ===========================
    
    global_events = [
        {"event": "다보스 포럼", "date": "2025-01-20", "market": "Global"},
        {"event": "일본 중앙은행 금리결정", "date": "2025-01-24", "market": "Japan"},
        {"event": "유럽중앙은행 회의", "date": "2025-01-23", "market": "Europe"},
        {"event": "중국 GDP 발표", "date": "2025-01-17", "market": "China"},
        {"event": "일본 중앙은행 금리결정", "date": "2025-03-19", "market": "Japan"},
        {"event": "유럽중앙은행 회의", "date": "2025-03-06", "market": "Europe"},
        {"event": "G7 정상회의", "date": "2025-06-13", "market": "Global"},
        {"event": "일본 중앙은행 금리결정", "date": "2025-06-16", "market": "Japan"},
        {"event": "유럽중앙은행 회의", "date": "2025-06-12", "market": "Europe"},
        {"event": "중국 GDP 발표", "date": "2025-07-15", "market": "China"},
        {"event": "일본 중앙은행 금리결정", "date": "2025-09-20", "market": "Japan"},
        {"event": "유럽중앙은행 회의", "date": "2025-09-12", "market": "Europe"},
        {"event": "일본 중앙은행 금리결정", "date": "2025-12-19", "market": "Japan"},
    ]
    
    for event_info in global_events:
        events.append({
            "id": f"global_{event_info['date']}",
            "title": f"🌍 {event_info['event']}",
            "start": event_info["date"],
            "backgroundColor": "#8b5cf6",
            "borderColor": "#8b5cf6",
            "extendedProps": {
                "eventType": "economic",
                "description": f"글로벌 경제 이벤트: {event_info['event']}",
                "importance": "medium",
                "details": f"시장: {event_info['market']}\\n영향도: 글로벌",
                "market": event_info["market"]
            }
        })
    
    return events

def save_extended_events():
    """확장된 이벤트를 JSON 파일로 저장
    
    generate_extended_events 함수로 생성된 이벤트를 calendar_events.json 파일로 저장합니다.
    이벤트 타입별, 월별 통계도 출력합니다.
    
    Returns:
        list: 생성된 이벤트 목록
    """
    events = generate_extended_events()
    
    with open('calendar_events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {len(events)}개의 확장된 투자 이벤트가 생성되었습니다! (2025년 전체)")
    
    # 이벤트 타입별 개수 출력
    event_types = {}
    for event in events:
        event_type = event['extendedProps']['eventType']
        event_types[event_type] = event_types.get(event_type, 0) + 1
    
    print("\\n📊 이벤트 타입별 개수:")
    for event_type, count in event_types.items():
        type_names = {
            'earnings': '실적발표',
            'dividend': '배당',
            'economic': '경제지표',
            'crypto': '가상화폐',
            'holiday': '공휴일'
        }
        print(f"  {type_names.get(event_type, event_type)}: {count}개")
    
    # 월별 이벤트 개수 출력
    monthly_counts = {}
    for event in events:
        month = event['start'][:7]  # YYYY-MM 형식
        monthly_counts[month] = monthly_counts.get(month, 0) + 1
    
    print("\\n📅 월별 이벤트 개수:")
    for month in sorted(monthly_counts.keys()):
        print(f"  {month}: {monthly_counts[month]}개")
    
    return events

if __name__ == "__main__":
    save_extended_events()