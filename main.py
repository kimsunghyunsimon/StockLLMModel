import os
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv

# 1. 환경 변수 로드
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    print("오류: .env 파일에서 GOOGLE_API_KEY를 찾을 수 없습니다.")
    exit()

genai.configure(api_key=API_KEY)

def analyze_stock_sentiment(company_name):
    # 2. 모델 설정
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    prompt = f"""
    Google Search 도구를 사용하여 지난 24시간 동안의 '{company_name}' 관련 주요 뉴스 기사 5개를 검색하세요.
    각 기사를 분석하여 주가에 미칠 영향을 다음 세 가지 중 하나로 분류하세요:
    - positive (긍정): 실적 호조, 수주 계약, 목표가 상향 등
    - negative (부정): 실적 악화, 소송, 규제, 목표가 하향 등
    - neutral (중립): 단순 시황, 단순 일정, 주가 영향 없음
    
    반드시 아래와 같은 JSON 리스트 형식으로만 응답하세요 (마크다운 없이 순수 JSON만):
    [
        {{"title": "기사 제목", "sentiment": "positive"}},
        {{"title": "기사 제목", "sentiment": "neutral"}}
    ]
    """

    try:
        response = model.generate_content(prompt, tools='google_search_retrieval')
        
        # 데이터 파싱
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        news_data = json.loads(clean_text)
        
        # 인덱스 계산
        pos_count = sum(1 for news in news_data if news['sentiment'] == 'positive')
        neg_count = sum(1 for news in news_data if news['sentiment'] == 'negative')
        total_count = len(news_data)

        if total_count == 0:
            return None

        sentiment_index = (pos_count - neg_count) / total_count
        
        # 결과 출력 (한 줄 요약 스타일)
        print(f"📊 {company_name:^10} | 지수: {sentiment_index:>5.2f} | (긍정 {pos_count} / 부정 {neg_count} / 전체 {total_count})")
        
        return sentiment_index

    except Exception as e:
        print(f"❌ {company_name:^10} | 분석 실패 ({e})")
        return None

if __name__ == "__main__":
    # ---------------------------------------------------------
    # 📝 여기에 분석하고 싶은 종목들을 적어주세요!
    # ---------------------------------------------------------
    my_portfolio = [
        "삼성전자", 
        "SK하이닉스", 
        "현대차", 
        "LG에너지솔루션", 
        "POSCO홀딩스",
        "NAVER",
        "카카오",
        "한미반도체",
        "알테오젠",
        "셀트리온"
    ]
    
    print(f"\n🚀 총 {len(my_portfolio)}개 종목의 뉴스 심리 분석을 시작합니다...\n")
    print("-" * 60)
    print(f"{'종목명':^10} | {'심리지수':^5} | {'상세 내용'}")
    print("-" * 60)

    for stock in my_portfolio:
        analyze_stock_sentiment(stock)
        # 구글 API 과부하 방지를 위해 1~2초 정도 쉬어줍니다.
        time.sleep(2) 
        
    print("-" * 60)
    print("✅ 분석이 모두 완료되었습니다.")