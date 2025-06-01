# InvestCalendar - 스마트한 투자 일정 관리 서비스 📈

한국투자증권 API와 Perplexity AI를 활용한 포괄적인 투자 캘린더 서비스

## 🚀 프로젝트 소개

InvestCalendar는 한국투자증권 Open API와 Perplexity AI를 활용하여 투자자들이 중요한 투자 일정을 놓치지 않도록 도와주는 종합 투자 서비스입니다. 국내외 주식, 가상화폐, 환율 등 모든 투자 관련 데이터를 실시간으로 제공합니다.

### ✨ 핵심 기능

- 📊 **실시간 투자 데이터** - 국내외 주식, 가상화폐, 환율 실시간 조회
- 🎯 **AI 투자 설명** - Perplexity AI를 통한 금융 용어 및 이벤트 설명
- 📅 **포괄적 투자 캘린더** - 실적발표, 배당, 경제지표 등 모든 투자 일정
- 🌍 **글로벌 시장 데이터** - 미국, 일본, 홍콩 등 해외 주식 시장 지원
- 💰 **가상화폐 지원** - 비트코인, 이더리움 등 주요 암호화폐 데이터
- 🎨 **다크모드 지원** - 사용자 편의를 위한 테마 전환
- 📱 **완전 반응형** - 모바일, 태블릿, 데스크톱 최적화

## 🛠 기술 스택

### Backend

- **FastAPI** - 고성능 비동기 웹 프레임워크
- **SQLAlchemy** - ORM 및 데이터베이스 관리
- **Pydantic** - 데이터 검증 및 설정 관리
- **APScheduler** - 백그라운드 스케줄링
- **aiohttp** - 비동기 HTTP 클라이언트
- **python-jose** - JWT 토큰 인증
- **passlib** - 패스워드 해싱

### Frontend

- **Tailwind CSS** - 유틸리티 기반 CSS 프레임워크
- **Alpine.js** - 가벼운 반응형 JavaScript 프레임워크
- **FullCalendar** - 강력한 캘린더 라이브러리
- **Font Awesome** - 아이콘 시스템

### 외부 API

- **한국투자증권 Open API** - 실시간 주식 데이터
- **Upbit API** - 가상화폐 데이터
- **Perplexity AI API** - AI 투자 설명 서비스

## 🏗 프로젝트 구조

```
invest-calendar/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/     # API 엔드포인트
│   ├── core/
│   │   ├── config.py          # 설정 관리
│   │   └── scheduler.py       # 백그라운드 작업
│   ├── db/
│   │   ├── models.py          # 데이터베이스 모델
│   │   └── session.py         # DB 세션 관리
│   ├── schemas/               # Pydantic 스키마
│   └── services/              # 비즈니스 로직
│       ├── kis_api.py         # 한국투자증권 API
│       └── perplexity_api.py  # Perplexity AI API
├── templates/
│   └── index.html             # 메인 웹페이지
├── calendar_events.json       # 실제 캘린더 이벤트 데이터
├── main.py                    # FastAPI 앱 진입점
└── requirements.txt           # 파이썬 의존성
```

## 🚀 시작하기

### 1. 환경 설정

```bash
# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 추가:

```env
# 한국투자증권 API
KIS_APP_KEY=your_app_key
KIS_APP_SECRET=your_app_secret
KIS_API_BASE_URL=https://openapi.koreainvestment.com:9443
KIS_ENV=vts

# Perplexity AI API
PERPLEXITY_API_KEY=your_perplexity_api_key

# 데이터베이스
DATABASE_URL=sqlite:///./invest_calendar.db

# 보안
SECRET_KEY=your-secret-key-change-this-in-production
```

### 3. 애플리케이션 실행

```bash
# 개발 서버 실행
python main.py
```

브라우저에서 `http://localhost:8000` 접속

## 📡 주요 API 엔드포인트

### 주식 데이터
- `GET /api/v1/stocks/price/{stock_code}` - 실시간 주가 조회
- `GET /api/v1/stocks/overseas/us` - 미국 주식 데이터
- `GET /api/v1/stocks/crypto` - 가상화폐 데이터
- `GET /api/v1/stocks/exchange-rates` - 환율 정보

### AI 설명 서비스
- `POST /api/v1/stocks/ai-explain/term` - 금융 용어 설명
- `POST /api/v1/stocks/ai-explain/event` - 시장 이벤트 설명
- `GET /api/v1/stocks/ai-explain/stock/{stock_code}` - 종목 분석

### 캘린더
- `GET /api/v1/calendar/events` - 투자 일정 조회
- `GET /api/v1/calendar/events/today` - 오늘의 주요 일정

## 🎯 주요 특징

### 실제 데이터 100% 활용
- 모든 샘플 데이터 제거
- 한국투자증권 API를 통한 실시간 주가 데이터
- Upbit API를 통한 실시간 가상화폐 데이터
- 실제 경제 지표 및 기업 일정 반영

### AI 기반 투자 설명
- Perplexity AI를 활용한 금융 용어 해설
- 복잡한 투자 개념을 초보자도 이해하기 쉽게 설명
- 실시간 시장 이벤트 분석 및 투자 포인트 제공

### 포괄적 시장 커버리지
- 국내 주식 (KOSPI, KOSDAQ)
- 해외 주식 (미국, 일본, 홍콩 등)
- 가상화폐 (비트코인, 이더리움 등)
- 환율 및 경제 지표

## 📱 UI/UX 특징

- **다크모드 지원** - 사용자 선호에 따른 테마 전환
- **색상 코딩** - 이벤트 타입별 직관적인 색상 구분
- **실시간 업데이트** - 주요 지수 및 데이터 자동 갱신
- **반응형 디자인** - 모든 디바이스에서 최적화된 경험

## 🔧 최근 업데이트 (2025.01)

### 코드 최적화
- 불필요한 의존성 제거 (pandas, numpy, requests 등)
- 사용하지 않는 코드 정리
- requirements.txt 간소화 (25개 → 12개 패키지)

### 기능 개선
- Perplexity AI 통합으로 투자 교육 기능 강화
- 실제 데이터만 사용하도록 완전 리팩토링
- 다크모드 및 이벤트 색상 코딩 수정

## 🚧 향후 계획

- 포트폴리오 관리 기능
- 실시간 알림 시스템
- 모바일 앱 개발
- 고급 차트 및 기술적 분석

## 📄 라이선스

MIT License

---

**Made with ❤️ for Korean Investors**