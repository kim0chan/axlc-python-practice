import sys
import os
from typing import List

# 부모 디렉토리를 path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.llm.openai_client import OpenAiLlmClient
from common.llm.models import ChatMessage
from common.ui import console, print_message, print_info, loading_spinner, Theme
from step3.meeting_service import MeetingService
from step4.tool_registry import ToolRegistry, FunctionalTool
from step6.guardrail import Guardrail

meeting_service = MeetingService()
tool_registry = ToolRegistry()
llm_client = OpenAiLlmClient()
guardrail = Guardrail(llm_client)

is_guardrail_enabled = False

def process_agent_loop(messages: List[ChatMessage]):
    while True:
        with loading_spinner("LLM은 생각중..."):
            response_msg = llm_client.ask_with_tools(
                messages, 
                tools=tool_registry.get_tool_specifications()
            )
        
        messages.append(response_msg)

        if response_msg.tool_calls:
            console.print("\n[Agent Thinking] 도구를 사용해야겠어...", style=Theme.ASSISTANT)
            for tool_call in response_msg.tool_calls:
                console.print(f">> Executing Tool: {tool_call.function.name}", style=Theme.WARNING)
                result = tool_registry.handle_tool_call(tool_call)
                console.print(f">> Result: {result}", style=Theme.HEADER)
                messages.append(ChatMessage(
                    role="tool", 
                    content=result, 
                    tool_call_id=tool_call.id, 
                    name=tool_call.function.name
                ))
            continue

        if response_msg.content:
            print_message(response_msg)
        break

def main():
    global is_guardrail_enabled
    
    # 도구 등록
    tool_registry.register(FunctionalTool(
        meeting_service.create_meeting, "create_meeting", "새로운 미팅 예약을 생성합니다."
    ))
    tool_registry.register(FunctionalTool(
        meeting_service.update_meeting, "update_meeting", "기존 미팅 예약을 수정합니다. 예약 ID가 필수입니다. ID를 모르면 목록을 먼저 조회하세요."
    ))
    tool_registry.register(FunctionalTool(
        meeting_service.delete_meeting, "delete_meeting", "미팅 예약을 취소합니다. 예약 ID가 필수입니다."
    ))
    tool_registry.register(FunctionalTool(
        meeting_service.get_meeting_list, "list_meetings", "현재 예약된 모든 미팅 목록을 조회합니다."
    ))

    console.print_header("[Step 6] 가드레일 통합 에이전트 데모")
    console.print("'guard on' 또는 'guard off'을 입력하여 가드레일을 제어하세요.\n", style=Theme.SYSTEM)

    messages = [ChatMessage(role="system", content="당신은 스마트 오피스의 미팅 예약 비서입니다.")]

    while True:
        meetings = meeting_service.find_all_meetings()
        if meetings:
            console.print(f"\n{Theme.HEADER}--- 현재 예약된 회의 목록 ---{Theme.RESET}")
            for m in meetings:
                console.print(f" {m}", style=Theme.SYSTEM)
            console.print(f"{Theme.HEADER}----------------------------{Theme.RESET}\n")
        else:
            console.print(f"\n{Theme.SYSTEM}(현재 예약된 회의가 없습니다.){Theme.RESET}\n")

        status_text = "🛡️ ON" if is_guardrail_enabled else "🛡️ OFF"
        status_style = Theme.SUCCESS if is_guardrail_enabled else Theme.ERROR
        
        # 사용자 입력 (가드레일 상태 표시)
        user_input = console.input(f"[{status_text}] [User]: ", style=status_style).strip()

        if user_input.lower() == "exit":
            print_info("대화를 종료합니다. Bye!")
            break

        if user_input.lower() == "guard on":
            is_guardrail_enabled = True
            print_info("가드레일이 활성화되었습니다!")
            continue
        elif user_input.lower() == "guard off":
            is_guardrail_enabled = False
            print_info("가드레일이 비활성화되었습니다!")
            continue


        # 🌟 가드레일 체크
        if is_guardrail_enabled:
            is_safe = guardrail.check_input(user_input)
            
            if not is_safe:
                console.print("[System] ⛔ 죄송합니다. 부적절하거나 주제에 맞지 않는 요청은 처리할 수 없습니다.", style=Theme.ERROR)
                continue

        messages.append(ChatMessage(role="user", content=user_input))
        process_agent_loop(messages)

if __name__ == "__main__":
    main()
