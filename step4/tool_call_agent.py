import sys
import os
from datetime import datetime
from typing import List

# 부모 디렉토리를 path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.llm.openai_client import OpenAiLlmClient
from common.llm.models import ChatMessage
from common.ui import console, print_message, print_info, loading_spinner, Theme
from step3.meeting_service import MeetingService
from step4.tool_registry import ToolRegistry, FunctionalTool
from rich.panel import Panel
from rich.table import Table

meeting_service = MeetingService()
tool_registry = ToolRegistry()
llm_client = OpenAiLlmClient()

def print_meeting_list():
    meetings = meeting_service.find_all_meetings()
    table = Table(title="📅 현재 예약된 미팅 목록", show_header=True, header_style="bold magenta")
    table.add_column("No.", style="dim", width=4)
    table.add_column("예약 상세 정보", style="cyan")

    if not meetings:
        table.add_row("-", "현재 예약된 미팅이 없습니다.")
    else:
        for i, m in enumerate(meetings, 1):
            table.add_row(str(i), m)

    console.print(Panel(table, expand=False, border_style="cyan"))

def build_system_prompt():
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    day_of_week = now.strftime("%A")
    
    return f"""
당신은 스마트 오피스의 미팅 예약 비서입니다.
현재는 {today_str} ({day_of_week})입니다.

# 가이드라인
- 사용자가 예약을 요청하거나, 변경/취소를 원할 때 제공된 도구를 사용하세요.
- **수정이나 취소 시 예약 번호(ID)를 모른다면, 반드시 `list_meetings` 도구를 먼저 호출하여 ID를 확인하세요.**
- 예약 가능 여부를 묻는다면 목록을 조회하여 판단하세요.
- 도구 실행 결과(SUCCESS/ERROR)를 보고 사용자에게 최종 결과를 친절하게 안내하세요.
- 예약과 관련 없는 대화는 평범하게 이어가세요.
"""

def process_agent_loop(messages: List[ChatMessage]):
    """
    AI Agent Loop: Tool Call이 없을 때까지 LLM과 대화하며 도구를 실행
    """
    while True:
        # 1. LLM에게 현재 상황 질문 (도구 명세 포함)
        with loading_spinner("LLM은 생각중..."):
            response_msg = llm_client.ask_with_tools(
                messages, 
                tools=tool_registry.get_tool_specifications()
            )
        
        # 대화 히스토리에 AI의 응답 추가
        messages.append(response_msg)

        # 🌟 Case A: LLM이 도구 사용을 요청함 (Tool Call)
        if response_msg.tool_calls:
            console.print("[Agent Thinking] 도구를 사용해야겠어...", style=Theme.ASSISTANT)

            for tool_call in response_msg.tool_calls:
                console.print(f">> Executing Tool: {tool_call.function.name}", style=Theme.WARNING)
                console.print(f"   Args: {tool_call.function.arguments}", style=Theme.SYSTEM)

                # 2. 실제 도구 실행
                result = tool_registry.handle_tool_call(tool_call)
                console.print(f">> Result: {result}", style=Theme.INFO)

                # 예약 성공 시 목록 다시 출력
                if "SUCCESS" in result:
                    print_meeting_list()

                # 3. 실행 결과를 다시 대화 히스토리에 추가 (role="tool")
                messages.append(ChatMessage(
                    role="tool", 
                    content=result, 
                    tool_call_id=tool_call.id, 
                    name=tool_call.function.name
                ))

            # 도구 실행 결과를 바탕으로 LLM에게 다시 물어봄 (Next Loop)
            continue

        # 🌟 Case B: 최종 응답 (사용자에게 출력)
        if response_msg.content:
            print_message(response_msg)
        break

def main():
    # 🌟 1. 도구 등록
    tool_registry.register(FunctionalTool(
        meeting_service.create_meeting, "create_meeting", "새로운 미팅 예약을 생성합니다."
    ))
    tool_registry.register(FunctionalTool(
        meeting_service.update_meeting, "update_meeting", "기존 미팅 예약을 수정합니다. 예약 ID가 필수입니다."
    ))
    tool_registry.register(FunctionalTool(
        meeting_service.delete_meeting, "delete_meeting", "미팅 예약을 취소합니다. 예약 ID가 필수입니다."
    ))
    tool_registry.register(FunctionalTool(
        meeting_service.get_meeting_list, "list_meetings", "현재 예약된 모든 미팅 목록을 조회합니다."
    ))

    console.print_header("[Step 4] Tool Call 에이전트: 스마트 비서 v2")
    print_info("목표: LLM에게 직접 도구를 쥐어주고 스스로 문제를 해결하게 합니다.\n")
    
    print_meeting_list()
    
    messages = [ChatMessage(role="system", content=build_system_prompt())]

    while True:
        # 사용자 입력
        user_input = console.input("[User]: ")
        
        if user_input.lower() == "exit":
            print_info("대화를 종료합니다. Bye!")
            break

        messages.append(ChatMessage(role="user", content=user_input))

        # 에이전트 루프 시작
        process_agent_loop(messages)

if __name__ == "__main__":
    main()
