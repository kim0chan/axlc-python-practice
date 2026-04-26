import sys
import os

# 부모 디렉토리를 path에 추가해 common을 찾을 수 있게 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.llm.openai_client import OpenAiLlmClient
from common.llm.models import ChatMessage
from common.ui import console, loading_spinner, print_message, print_info

def main():
    """
    Step 0: First API Call
    LLM API를 호출하여 Stateless 특성을 이해하기 위한 실습입니다.
    """

    # 클라이언트 생성
    client = OpenAiLlmClient()
    console.print(f"\n[bold cyan]=== [Step 0] LLM과 대화를 시작합니다 (종료하려면 'exit' 입력) ===[/]\n")

    while True:
        # 1. 사용자 입력 받기
        user_input = console.input(f"[bold blue][User]: [/]")
        
        if user_input.lower() == "exit":
            print_info("대화를 종료합니다. Bye!")
            break

        # 2. 메시지 구성
        messages = [ChatMessage(role="user", content=user_input)]

        # 3. API 호출
        with loading_spinner("LLM은 생각중..."):
            ai_response = client.ask(messages)

        # 4. 응답 출력
        print_message(ai_response)

if __name__ == "__main__":
    main()
