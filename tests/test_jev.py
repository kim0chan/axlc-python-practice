import os
import sys
from dotenv import load_dotenv

# 프로젝트 루트를 path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.llm.jev_client import JevClient
from common.ui import console, Theme

def test_jev_features():
    load_dotenv()
    
    try:
        client = JevClient()
    except ValueError as e:
        console.print(f"[Error] {e}", style=Theme.ERROR)
        return

    console.print_header("Jev (System One) API 기능 테스트")

    # 1. Choice Test: 의도 분류
    console.print("\n[1] Choice API Test: 의도 분류", style="bold cyan")
    state_choice = "내일 오전 10시에 회의실 A 예약해줄래?"
    criteria = {
        "meeting": "회의 예약 및 일정 관리",
        "email": "이메일 작성 및 확인",
        "chat": "단순 일상 대화"
    }
    result_choice = client.choice(state_choice, "이 요청의 카테고리를 선택하세요.", criteria)
    console.print(f"Input: {state_choice}")
    console.print(f"Result: {result_choice}", style=Theme.SUCCESS)

    # 2. Noul Test: 이진 판단 (확률)
    console.print("\n[2] Noul API Test: 긴급도 판단", style="bold cyan")
    state_noul = "서버가 지금 죽었어! 당장 확인해줘!"
    result_noul = client.noul(state_noul, "이 메시지는 긴급한 조치가 필요한가요?")
    console.print(f"Input: {state_noul}")
    console.print(f"Probability (Yes): {result_noul:.2f}", style=Theme.SUCCESS)

    # 3. Score Test: 정성적 평가 (수치화)
    console.print("\n[3] Score API Test: 감정 분석 (점수)", style="bold cyan")
    state_score = "배송이 너무 늦어서 정말 실망했어요. 다신 안 쓸 것 같네요."
    rubric = [
        "매우 만족",
        "보통",
        "매우 불만족"
    ]
    # Score는 0 ~ (n-1) 사이의 가중 평균 점수를 반환 (여기서는 0:만족, 2:불만족)
    result_score = client.score(state_score, "고객의 불만 정도를 측정하세요.", rubric)
    console.print(f"Input: {state_score}")
    console.print(f"Score (0=만족, 2=불만족): {result_score:.2f}", style=Theme.SUCCESS)

    # 4. Multi-Decision Test: 한 번에 여러 개 묻기
    console.print("\n[4] Multi-Decision Test: 병렬 판단", style="bold cyan")
    from common.llm.jev_models import JevQuestion
    
    state_multi = "대표님, 이번 달 매출 보고서가 준비되었습니다. 검토 부탁드립니다."
    questions = {
        "intent": JevQuestion(type="choice", instructions="의도 분류", criteria={"report": "보고서 제출", "ask": "질문"}),
        "is_formal": JevQuestion(type="noul", instructions="격식 있는 말투인가요?"),
        "importance": JevQuestion(type="score", instructions="중요도 평가", criteria=["낮음", "중간", "높음"])
    }
    
    multi_res = client.decide(state_multi, questions)
    console.print(f"Input: {state_multi}")
    console.print(f"Answers: {multi_res.answers}", style=Theme.SUCCESS)

if __name__ == "__main__":
    test_jev_features()
