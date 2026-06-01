import sys
import os
import re

from common.llm.openai_client import OpenAiLlmClient

# 부모 디렉토리를 path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.llm.client import LlmClient
from common.llm.models import ChatMessage
from common.ui import console, Theme

class SimpleEval:
    def __init__(self, judge_client: LlmClient):
        self.judge_client = judge_client

    def evaluate_faithfulness(self, context: str, answer: str) -> int:
        """
        답변의 충실도(Faithfulness)를 1~5점으로 평가합니다.
        """
        console.print("\n[Eval] 답변의 충실도를 평가 중입니다...", style=Theme.HEADER)

        prompt = f"""
당신은 LLM이 생성한 답변의 '충실도(Faithfulness)'를 채점합니다.
주어진 '맥락(Context)'에 비추어 볼 때, '답변(Answer)'이 얼마나 사실에 근거했는지 판단하여 1~5점의 점수를 내려주세요.

[채점 기준]
- 5점: 답변의 모든 내용이 맥락에 정확히 명시되어 있음.
- 3점: 답변의 일부 내용이 맥락에 없거나 추측이 섞여 있음.
- 1점: 답변이 맥락과 상관없거나 거짓 정보를 포함하고 있음(환각 현상).

맥락: "{context}"
답변: "{answer}"

결과는 '점수: [정수]' 형식으로만 한 줄로 대답하세요 (예: 점수: 5).
결과:"""

        result_msg = self.judge_client.ask([ChatMessage(role="user", content=prompt)])
        
        try:
            # 결과에서 점수만 추출
            if not result_msg.content:
                return 1
                
            match = re.search(r"(\d+)", result_msg.content)
            if match:
                return int(match.group(1))
            return 1
        except Exception as e:
            console.print(f"[Eval] 점수 파싱 에러! 결과: {result_msg.content if result_msg else 'None'}", style=Theme.ERROR)
            return 1

def main():
    client = OpenAiLlmClient()
    evaluator = SimpleEval(client)

    # 테스트 케이스들
    test_cases = [
        ("회의실 A는 오후 2시부터 4시까지 예약이 불가능합니다.", "죄송합니다. 회의실 A는 오후 3시에 예약할 수 없습니다."),
        ("회의실 B는 오전에만 사용 가능합니다.", "회의실 B는 오후 5시에 예약 가능합니다. 커피도 무료로 제공됩니다."),
        ("회의실 B는 짜파게티 파티를 위해 예약되었습니다.", "청양고추와 올리브유로 고추기름을 내어 볶으면 더 맛있습니다.")
    ]

    for i, (ctx, ans) in enumerate(test_cases, 1):
        console.print(f"\n테스트 케이스 {i}", style=Theme.WARNING)
        console.print(f"Context: {ctx}", style=Theme.SYSTEM)
        console.print(f"Answer: {ans}", style=Theme.SYSTEM)
        
        score = evaluator.evaluate_faithfulness(ctx, ans)
        
        score_style = Theme.SUCCESS if score >= 4 else Theme.WARNING if score >= 3 else Theme.ERROR
        console.print(f"-> [평가 결과] 충실도 점수: {score}/5", style=score_style)

if __name__ == "__main__":
    main()
