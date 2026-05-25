import sys
import os
from typing import List
from dataclasses import dataclass, field

# 부모 디렉토리를 path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.llm.openai_client import OpenAiLlmClient
from common.llm.models import ChatMessage
from common.ui import console, print_message, print_info, loading_spinner, print_warning, Theme
from step4.tool_registry import ToolRegistry, FunctionalTool, McpTool
from step3.meeting_service import MeetingService
from common.mcp_client import MultiMcpManager

# 🌟 에이전트 상태 관리 객체
@dataclass
class AgentState:
    messages: List[ChatMessage]
    max_iterations: int = 10
    iteration_count: int = 0
    is_finished: bool = False
    metadata: dict = field(default_factory=dict)

meeting_service = MeetingService()
tool_registry = ToolRegistry()
llm_client = OpenAiLlmClient()

def build_system_prompt():
    return """
당신은 다양한 도구들을 능숙하게 사용하는 유능한 '자율 에이전트'입니다.
사용자의 요청을 해결하기 위해 ReAct(Reasoning and Acting) 패턴을 사용하여 문제를 해결하세요.

# ReAct 패턴 단계:
1. **Thought**: 현재 상황을 분석하고 어떤 도구가 필요한지, 왜 필요한지 생각합니다.
2. **Action**: 필요한 도구를 호출합니다.
3. **Observation**: 도구의 실행 결과를 꼼꼼히 확인하고 다음 단계를 결정합니다.
4. 문제가 해결되기 전까지는 위의 1~3단계를 반복하세요.
5. **Final Answer**: 모든 작업이 완료되면 최종 답변을 제공합니다.

# 주의사항:
- 매 단계마다 반드시 'Thought:'를 적어 사고 과정을 보여주세요.
- 최종 답변을 할 때는 'Final Answer:'를 앞에 붙여주세요.
- 도구 실행 중 에러가 나면, 당황하지 말고 에러 메시지를 바탕으로 다시 시도하거나 사용자에게 질문하세요.
"""

def run_agent_loop(state: AgentState):
    """
    에이전트가 목표를 달성할 때까지 루프를 돌며 생각하고 행동합니다.
    """
    while state.iteration_count < state.max_iterations and not state.is_finished:
        state.iteration_count += 1
        console.print(f"\n[Iteration {state.iteration_count}] 고민 중...", style=Theme.SYSTEM)

        # 1. LLM 호출 (현재까지의 기록 전달)
        with loading_spinner("에이전트가 생각하고 있습니다..."):
            response_msg = llm_client.ask_with_tools(
                state.messages, 
                tools=tool_registry.get_tool_specifications()
            )
        
        state.messages.append(response_msg)

        # 🌟 2. 사고 과정(Thought) 및 종료 판단
        if response_msg.content:
            content = response_msg.content
            # Thought 출력
            if "Thought:" in content:
                thought = content.split("Thought:")[1].split("Action:")[0].split("Final Answer:")[0].strip()
                console.print(f"💡 [Thought]: {thought}", style=Theme.ASSISTANT)
            
            # Final Answer가 있으면 종료
            if "Final Answer:" in content:
                final_answer = content.split("Final Answer:")[1].strip()
                print_message(ChatMessage(role="assistant", content=final_answer))
                state.is_finished = True
                continue

        # 🌟 3. 행동(Action) 및 관찰(Observation)
        if response_msg.tool_calls:
            for tool_call in response_msg.tool_calls:
                tool_name = tool_call.function.name
                tool_args = tool_call.function.arguments
                console.print(f"[Action]: {tool_name} 실행 ({tool_args})", style=Theme.WARNING)

                try:
                    # 도구 실행 (Observation)
                    observation = tool_registry.handle_tool_call(tool_call)
                    display_obs = (observation[:200] + "...") if len(observation) > 200 else observation
                    console.print(f"[Observation]: {display_obs}", style=Theme.INFO)
                except Exception as e:
                    # 에러 발생 시 LLM에게 전달하여 스스로 해결하게 유도
                    observation = f"Error: 도구 실행 중 오류가 발생했습니다. ({str(e)})"
                    print_warning(f"에러를 에이전트에게 전달합니다: {observation}")

                # 실행 결과 기록
                state.messages.append(ChatMessage(
                    role="tool", 
                    content=observation, 
                    tool_call_id=tool_call.id, 
                    name=tool_name
                ))
        else:
            # Tool Call이 없는데 Final Answer도 없으면 루프 종료 방지 위해 체크
            if not response_msg.content:
                state.is_finished = True

def main():
    # 1. 일반 도구 등록 (Internal Tools)
    tool_registry.register(FunctionalTool(meeting_service.create_meeting, "create_meeting", "회의 예약 생성"))
    tool_registry.register(FunctionalTool(meeting_service.get_meeting_list, "list_meetings", "예약 목록 조회"))

    # 2. 멀티 MCP 서버 등록 (Multi-MCP Setup)
    mcp_manager = MultiMcpManager()
    
    # 🌟 여기에 서버를 추가하기
    # mcp_manager.add_server("fetch", ["npx", "-y", "mcp-server-fetch-typescript"])
    # Filesystem 서버는 접근을 허용할 디렉터리 경로를 인자로 넘겨줘야 함!
    # project_root = os.getcwd()
    # mcp_manager.add_server("file-system", ["npx", "-y", "@modelcontextprotocol/server-filesystem", project_root])

    # 등록된 모든 MCP 서버의 도구들을 ToolRegistry에 자동 등록
    for client, tool_info in mcp_manager.get_all_tools():
        tool_registry.register(McpTool(
            client=client,
            name=tool_info['name'],
            description=tool_info['description'],
            input_schema=tool_info['inputSchema']
        ))

    console.print_header("[Step 5] Agentic Workflow (Python Edition)")
    print_info("목표: ReAct 패턴을 사용하여 스스로 도구를 선택하고 문제를 해결하는 에이전트를 실습합니다.\n")
    print_info(f"현재 등록된 도구 수: {len(tool_registry.tools)}개")
    
    initial_messages = [ChatMessage(role="system", content=build_system_prompt())]

    try:
        while True:
            user_input = console.input("[User]: ")
            
            if user_input.lower() in ["exit", "quit"]:
                print_info("대화를 종료합니다. Bye~")
                break

            # 새로운 상태로 루프 시작
            state = AgentState(messages=initial_messages + [ChatMessage(role="user", content=user_input)])
            run_agent_loop(state)
    finally:
        # 종료 시 모든 MCP 서버 정리 (프로세스 종료)
        mcp_manager.close_all()


if __name__ == "__main__":
    main()
