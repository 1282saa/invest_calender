"""
AI 기능 테스트 스크립트
Perplexity API와 프롬프트 테스트
"""
import asyncio
import sys
import os
sys.path.append('.')

from app.services.perplexity_api import perplexity_client

async def test_ai_explanations():
    print("🤖 AI 설명 기능 테스트 시작...")
    
    # 1. 경제 지표 설명 테스트
    print("\n1️⃣ 경제 지표 설명 테스트:")
    try:
        result = await perplexity_client.explain_financial_term(
            term="5월 고용동향",
            context="고용률과 실업률 발표로 주식시장에 영향"
        )
        print(f"✅ 성공: {result['success']}")
        if result['success']:
            print(f"📝 설명:\n{result['explanation']}")
        else:
            print(f"❌ 오류: {result['explanation']}")
    except Exception as e:
        print(f"❌ 예외 발생: {e}")
    
    print("\n" + "="*80)
    
    # 2. 기업 실적 설명 테스트
    print("\n2️⃣ 기업 실적 설명 테스트:")
    try:
        result = await perplexity_client.explain_market_event(
            event_title="삼성전자 실적발표",
            event_details="2024년 4분기 실적 발표, 현재주가 70,000원"
        )
        print(f"✅ 성공: {result['success']}")
        if result['success']:
            print(f"📝 설명:\n{result['explanation']}")
        else:
            print(f"❌ 오류: {result['explanation']}")
    except Exception as e:
        print(f"❌ 예외 발생: {e}")
    
    print("\n" + "="*80)
    
    # 3. 공시정보 설명 테스트
    print("\n3️⃣ 공시정보 설명 테스트:")
    try:
        result = await perplexity_client.explain_market_event(
            event_title="주요사항보고서",
            event_details="회사명: 삼성전자, 대규모내부거래 관련 공시"
        )
        print(f"✅ 성공: {result['success']}")
        if result['success']:
            print(f"📝 설명:\n{result['explanation']}")
        else:
            print(f"❌ 오류: {result['explanation']}")
    except Exception as e:
        print(f"❌ 예외 발생: {e}")
    
    print("\n" + "="*80)
    
    # 4. 종목 분석 테스트
    print("\n4️⃣ 종목 분석 테스트:")
    try:
        result = await perplexity_client.get_stock_analysis(
            stock_name="삼성전자",
            stock_code="005930",
            current_price="70,000"
        )
        print(f"✅ 성공: {result['success']}")
        if result['success']:
            print(f"📝 분석:\n{result['analysis']}")
        else:
            print(f"❌ 오류: {result['analysis']}")
    except Exception as e:
        print(f"❌ 예외 발생: {e}")

    print("\n🎯 AI 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(test_ai_explanations())