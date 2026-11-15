import sys
import os
import time

# 부모 디렉토리를 path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.llm.jev_client import JevClient
from common.llm.jev_models import JevQuestion
from common.ui import console, Theme

def main():
    client = JevClient()
    
    console.print_header("[Step 1-2] 영화 리뷰 감성 분류기 (Jev Batch)")
    console.print("목표: 모든 리뷰를 단 한 번의 API 호출(Batch)로 처리하여 지연 시간을 극한으로 줄입니다.\n")

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

    # 1. Batch 요청 구성
    # state에 리스트 전체를 넣고, questions에서 인덱스로 참조하거나 병렬 질문을 생성합니다.
    criteria = {
        "긍정적": "영화에 대해 칭찬하거나 만족하는 리뷰",
        "부정적": "영화에 대해 불평하거나 실망하는 리뷰"
    }

    questions = {}
    for i in range(len(reviews)):
        # Jev는 state가 리스트인 경우 각 질문의 instructions에서 해당 인덱스를 명시하거나,
        # 단순히 리스트 전체를 보고 각각 판단하게 할 수 있습니다. 
        # 여기서는 각 리뷰를 개별 질문으로 매핑합니다.
        questions[f"rev_{i}"] = JevQuestion(
            type="choice",
            instructions=f"리스트의 {i}번째 리뷰('{reviews[i][:15]}...')의 감성을 분류하세요.",
            criteria=criteria
        )

    # 2. 단 한 번의 호출 (Batch)
    start_time = time.perf_counter()
    response = client.decide(state=reviews, questions=questions)
    end_time = time.perf_counter()
    
    total_latency_ms = (end_time - start_time) * 1000

    # 3. 결과 출력
    positive_count = 0
    negative_count = 0

    for i in range(len(reviews)):
        answer = response.answers[f"rev_{i}"]
        sentiment = answer.choice
        
        color = Theme.SUCCESS if "긍정적" in sentiment else Theme.ERROR if "부정적" in sentiment else Theme.WARNING
        console.print(f"Review #{i+1}: \"{reviews[i][:30]}...\"")
        console.print(f"  └ Result: {sentiment}", style=color)
        
        if "긍정적" in sentiment:
            positive_count += 1
        elif "부정적" in sentiment:
            negative_count += 1

    console.print("\n" + "="*40, style=Theme.INFO)
    console.print(f"📊 최종 집계 결과 (Jev Batch)", style=Theme.INFO)
    console.print(f"총 리뷰 수: {len(reviews)}개")
    console.print(f"긍정 리뷰: {positive_count}개")
    console.print(f"부정 리뷰: {negative_count}개")
    console.print(f"총 소요 시간: {total_latency_ms:.2f}ms", style=Theme.WARNING)
    console.print("="*40, style=Theme.INFO)
    console.print(f"💡 [dim]한 번의 API 호출로 모든 판단이 완료되었습니다.[/]")

if __name__ == "__main__":
    main()
