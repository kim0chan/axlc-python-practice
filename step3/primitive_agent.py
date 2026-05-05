import sys
import os
import re
from datetime import datetime

# 부모 디렉토리를 path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.llm.openai_client import OpenAiLlmClient
from common.llm.models import ChatMessage
from common.ui import console, print_message, print_info, loading_spinner, ConsoleColor
from step3.meeting_service import MeetingService, CreateMeetingRequest
from rich.panel import Panel
from rich.table import Table

meeting_service = MeetingService()

def build_system_prompt():
    """
    현재 날짜와 요일을 포함한 시스템 프롬프트를 생성합니다.
    """
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    day_of_week = now.strftime("%A")
    
    return f"""
# Basic Information
- 당신은 스마트 오피스의 미팅 예약 에이전트입니다.
- 현재는 {today_str} ({day_of_week})입니다. 이 정보를 바탕으로 날짜를 추론하세요.

# Rules
- 이용자가 미팅 예약과 관련 없는 대화를 진행할 경우, 평범하게 대화를 이어가세요.
- 만약 미팅 예약을 위한 정보가 하나라도 부족하면 반드시 "NEED_INFO: {{부족한 정보에 대한 질문}}" 형식으로 답변하세요.
- 미팅 예약을 위한 모든 정보가 수집되었다면 반드시 "EXECUTE: CREATE_MEETING(date='...', time='...', attendees='...')" 형식으로 답변하세요.

# Scheduling A Meeting
사용자가 미팅 예약을 요청하면 다음 3가지 정보가 반드시 필요합니다:
1. 날짜 (예: 2026-02-11)
2. 시간 (예: 14:00)
3. 참석자 (예: 김철수, 이영희)

___
대화의 흐름에 따라 유연하게 대처하세요. 굿럭!
"""

def print_meeting_list():
    """
    현재 예약된 미팅 목록을 테이블로 출력
    """
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

def extract_value(command: str, key: str) -> str:
    """
    정규표현식을 사용하여 명령문에서 특정 키의 값을 추출
    """
    match = re.search(f"{key}='(.*?)'", command)
    return match.group(1) if match else ""

def execute_action(command: str) -> str:
    """
    문자열 명령을 해석하여 실제 서비스를 호출
    """
    if "CREATE_MEETING" in command:
        req = CreateMeetingRequest(
            date=extract_value(command, "date"),
            time=extract_value(command, "time"),
            attendees=extract_value(command, "attendees")
        )
        return meeting_service.create_meeting(req)
    return "ERROR: 알 수 없는 명령입니다."

def main():
    client = OpenAiLlmClient()
    
    console.print("\n[bold cyan]=== [Step 3] 원시 에이전트: 스마트 오피스 비서 ===[/]")
    print_info("목표: 미팅 예약에 필요한 정보를 수집하여 예약을 실행합니다.\n")
    
    print_meeting_list()
    
    messages = [ChatMessage(role="system", content=build_system_prompt())]

    while True:
        # 사용자 입력
        user_input = console.input(f"\n[bold blue][User]: [/]")
        
        if user_input.lower() == "exit":
            print_info("대화를 종료합니다. Bye!")
            break

        messages.append(ChatMessage(role="user", content=user_input))

        with loading_spinner("에이전트가 상황을 판단하는중..."):
            response = client.ask(messages)

        # 🌟 판단 결과 분석
        if response.content.startswith("NEED_INFO:"):
            question = response.content.replace("NEED_INFO:", "").strip()
            console.print(f"\n[bold yellow][Need Info][/] {question}")
            messages.append(ChatMessage(role="assistant", content=response.content))
            
        elif response.content.startswith("EXECUTE:"):
            console.print(f"\n[bold magenta][Agent Action][/] 명령을 인식했습니다! 시스템을 호출합니다...")
            console.print(f"[dim]>> {response.content}[/]")
            
            # 실제 액션 실행
            result = execute_action(response.content)
            
            # 실행 결과 출력 및 반영
            print_meeting_list()
            console.print(f"[bold cyan][System][/] {result}")

            # 실행 결과를 다시 히스토리에 추가
            messages.append(ChatMessage(role="assistant", content=response.content))
            messages.append(ChatMessage(role="user", content=f"시스템 실행 결과: {result}"))
            
        else:
            print_message(response)
            messages.append(ChatMessage(role="assistant", content=response.content))

if __name__ == "__main__":
    main()
