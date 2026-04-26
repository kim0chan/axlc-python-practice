import sys
import os

# 부모 디렉토리를 path에 추가해 common을 찾을 수 있게 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.llm.openai_client import OpenAiLlmClient
from common.llm.models import ChatMessage
from common.ui import console, loading_spinner, print_message, print_info

def main():
    """
    Step 1: Basic Context Management
    LLM의 Stateless 특성을 이해하고, List를 이용해 직접 대화 맥락을 관리하는 기초 실습입니다.
    """

    # 클라이언트 생성
    client = OpenAiLlmClient()

    # 🌟 1. 대화 히스토리 초기화 (시스템 메시지 추가)
    messages = [
        ChatMessage(role="system", content="당신은 유능한 파이썬 전문가입니다. 질문에 대해 친절하고 명확하게 답변하세요.")
    ]

    console.print("\n[bold cyan]=== [Step 1] 맥락을 기억하는 LLM 대화 (종료하려면 'exit' 입력) ===[/]\n")

    while True:
        # 2. 사용자 입력 받기 (색깔 입히기!)
        user_input = console.input(f"[bold blue][User]: [/]")

        if user_input.lower() == "exit":
            print_info("대화를 종료합니다. Bye!")
            break

        # 🌟 3. 사용자 메시지 추가
        messages.append(ChatMessage(role="user", content=user_input))

        # 최근 10개만 유지
        if len(messages) > 11:
            messages = [messages[0]] + messages[-10:]

        # 4. API 호출
        with loading_spinner("LLM은 생각중..."):
            ai_response = client.ask(messages)

        # 🌟 5. AI 응답 출력 및 히스토리에 추가
        print_message(ai_response)
        messages.append(ai_response)

if __name__ == "__main__":
    main()
