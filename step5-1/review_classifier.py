import sys
import os
import time

# 부모 디렉토리를 path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.llm.openai_client import OpenAiLlmClient
from common.llm.models import ChatMessage
from common.ui import console, Theme

def classify_review(client: OpenAiLlmClient, review_text: str):
    """
    단일 리뷰 텍스트를 입력받아 감성을 분류합니다. (Stateless)
    """
    messages = [
        ChatMessage(role="system", content=(
            "너는 영화 리뷰 감성 분류기야. "
            "입력된 리뷰를 분석해서 긍정적이면 '긍정적', 부정적이면 '부정적'이라고 딱 3글자로만 대답해. "
            "다른 미사여구는 절대 붙이지 마."
        )),
        ChatMessage(role="user", content=review_text)
    ]

    start_time = time.perf_counter()
    response = client.ask(messages)
    end_time = time.perf_counter()
    
    latency_ms = (end_time - start_time) * 1000
    return response.content.strip(), latency_ms

def main():
    client = OpenAiLlmClient() # 기본적으로 gpt-5-nano 사용
    
    console.print_header("[Step 1-2] 영화 리뷰 감성 분류기 (Python)")
    console.print("목표: LLM을 단순 분류기로 활용하여 성능(지연 시간)을 측정합니다.\n")

    reviews = [
        "진짜 인생 영화입니다... 보는 내내 눈물이 멈추지 않았어요. 😭",
        "돈 아까워요. 개연성도 없고 연기도 형편없네요. 비추입니다.",
        "영상미는 좋은데 스토리가 너무 뻔해요. 그냥 쏘쏘.",
        "배우들 연기력이 다했네요. 긴장감 넘쳐서 숨도 못 쉬고 봤습니다! 👍",
        "아... 내 아까운 2시간... 감독님 반성하세요.",
        "올해 본 영화 중 최고! 음악이랑 연출이 너무 환상적이에요.",
        "기대 안 하고 봤는데 의외로 꿀잼! 친구랑 가볍게 보기 좋아요.",
        "지루해서 중간에 잤습니다. 돈 주고 보기엔 좀 아깝네요.",
        "마지막 반전이 진짜 대박... 아직도 소름 돋아요. 꼭 보세요!",
        "원작 파괴 수준이네요. 원작 팬으로서 너무 실망스럽습니다."
    ]

    positive_count = 0
    negative_count = 0
    total_latency = 0

    for i, review in enumerate(reviews, 1):
        sentiment, latency = classify_review(client, review)
        total_latency += latency
        
        # 결과 출력
        color = Theme.SUCCESS if "긍정적" in sentiment else Theme.ERROR if "부정적" in sentiment else Theme.WARNING
        console.print(f"Review #{i}: \"{review[:30]}...\"")
        console.print(f"  └ Result: {sentiment} ({latency:.2f}ms)", style=color)
        
        if "긍정적" in sentiment:
            positive_count += 1
        elif "부정적" in sentiment:
            negative_count += 1

    avg_latency = total_latency / len(reviews)

    console.print("\n" + "="*40, style=Theme.INFO)
    console.print(f"📊 최종 집계 결과", style=Theme.INFO)
    console.print(f"총 리뷰 수: {len(reviews)}개")
    console.print(f"긍정 리뷰: {positive_count}개")
    console.print(f"부정 리뷰: {negative_count}개")
    console.print(f"평균 지연 시간: {avg_latency:.2f}ms", style=Theme.WARNING)

if __name__ == "__main__":
    main()
