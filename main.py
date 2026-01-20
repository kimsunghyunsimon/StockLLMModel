import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# 1. 환경 변수 로드 (API 키 보안)
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    print("오류: .env 파일에서 GOOGLE_API_KEY를 찾을 수 없습니다.")
    exit()

genai.configure(api_key=API_KEY)

def analyze_stock_sentiment(company_name):
    print(f"\n🔍 '{company_name}' 관련 최신 24시간 뉴스를 검색하고 분석 중입니다...")

    # 2. 모델 설정 (Google Search 도구 활성화)
    # gemini-2.0-flash-exp 또는 사용 가능한 최신 모델 사용
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    # 3. 프롬프트 설계 (JSON 포맷 강제)
    prompt = f"""
    당신은 주식 시장 분석 AI입니다.
    Google Search 도구를 사용하여 지난 24시간 동안의 '{company_name}' 관련 주요 뉴스 기사 10개를 검색하세요.
    
    각 기사를 분석하여 주가에 미칠 영향을 다음 세 가지 중 하나로 분류하세요:
    - positive (긍정): 실적 호조, 수주 계약, 목표가 상향 등
    - negative (부정): 실적 악화, 소송, 규제, 목표가 하향 등
    - neutral (중립): 단순 시황, 단순 일정, 주가 영향 없음
    
    반드시 아래와 같은 JSON 리스트 형식으로만 응답하세요 (마크다운 없이 순수 JSON만):
    [
        {{"title": "기사 제목1", "sentiment": "positive"}},
        {{"title": "기사 제목2", "sentiment": "neutral"}}
    ]
    """

    try:
        # 4. 검색 및 생성 요청
        response = model.generate_content(
            prompt,
            tools='google_search_retrieval'
        )
        
        # 5. 응답 데이터 파싱 (텍스트 -> JSON)
        # 가끔 마크다운 ```json ... ``` 이 포함될 수 있어 제거 처리
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        news_data = json.loads(clean_text)
        
        # 6. 인덱스 계산
        pos_count = sum(1 for news in news_data if news['sentiment'] == 'positive')
        neg_count = sum(1 for news in news_data if news['sentiment'] == 'negative')
        neutral_count = sum(1 for news in news_data if news['sentiment'] == 'neutral')
        total_count = len(news_data)

        if total_count == 0:
            return 0.0

        # 공식: (긍정 - 부정) / 총 기사수
        sentiment_index = (pos_count - neg_count) / total_count
        
        # 7. 결과 출력
        print(f"\n📊 [{company_name}] 분석 결과")
        print("-" * 40)
        print(f"총 검색 기사: {total_count}건")
        print(f"🟢 긍정: {pos_count} | 🔴 부정: {neg_count} | ⚪ 중립: {neutral_count}")
        print("-" * 40)
        print(f"📈 뉴스 심리 지수: {sentiment_index:.2f}")
        
        if sentiment_index > 0.3:
            print("💡 의견: 긍정적 모멘텀이 강합니다.")
        elif sentiment_index < -0.3:
            print("💡 의견: 부정적 이슈에 주의하세요.")
        else:
            print("💡 의견: 시장이 관망세이거나 중립적입니다.")

        return sentiment_index

    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
        return None

if __name__ == "__main__":
    # 테스트하고 싶은 종목 입력
    target_company = input("분석할 종목명을 입력하세요 (예: 삼성전자): ")
    analyze_stock_sentiment(target_company)