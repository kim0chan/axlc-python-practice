import sys
import os
import importlib
import traceback

from common.ui import console, Theme

# 프로젝트 루트를 path에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def show_menu():
    title = "AXLC Practice"
    padding = " " * 4
    line = "━" * (len(title) + 8)

    console.print(f"\n{line}", style=Theme.ASSISTANT)
    console.print(f"┃{padding}{title}{padding}┃", style=Theme.ASSISTANT)
    console.print(f"{line}\n", style=Theme.ASSISTANT)
    console.print(" 원하는 실습 단계를 선택해주세요.\n", style=Theme.SYSTEM)
    
    steps = {
        "0": ("Step 0: Stateless Chat (첫 API 호출)", "step0.stateless_chat"),
        "1": ("Step 1: Context Chat (대화 맥락 관리)", "step1.context_chat"),
        "2": ("Step 2: Agentic RAG (지식 기반 대화)", "step2.main"),
        "3": ("Step 3: Primitive Agent (원시 에이전트)", "step3.primitive_agent"),
        "4": ("Step 4: Tool Call Agent (도구를 사용하는 에이전트)", "step4.tool_call_agent"),
        "q": ("종료하기", None)
    }

    for key, (desc, _) in steps.items():
        console.print(f"  {key}: {desc}", style=Theme.HEADER)

    # 입력 받기
    choice = console.input("\n 선택 (기본: q): ", style=Theme.WARNING).strip().lower()
    if not choice: choice = "q"
    
    return steps.get(choice)

def main():
    while True:
        choice_info = show_menu()
        if not choice_info or choice_info[1] is None:
            console.print("\n고생하셨습니다.", style=Theme.WARNING)
            break
        
        module_path = choice_info[1]
        try:
            console.print(f"\n>>> {choice_info[0]} 실행 중...\n", style=Theme.SUCCESS)
            
            # 동적으로 모듈을 로드해서 실행
            # 이미 로드된 모듈이 있다면 reload해서 최신 상태를 반영
            if module_path in sys.modules:
                module = importlib.reload(sys.modules[module_path])
            else:
                module = importlib.import_module(module_path)
            
            # 각 모듈의 main() 함수를 실행
            if hasattr(module, "main"):
                module.main()
            else:
                console.print(f"에러: {module_path} 모듈에 main() 함수가 없습니다.", style=Theme.ERROR)
                
            console.print("\n--- 실습 완료 ---\n", style=Theme.SUCCESS)
            input("엔터를 누르면 메뉴로 돌아갑니다...")
            console.clear()
            
        except Exception as e:
            console.print(f"\n실행 중 오류 발생: {str(e)}", style=Theme.ERROR)
            traceback.print_exc()
            input("\n엔터를 누르면 메뉴로 돌아갑니다...")
            console.clear()

if __name__ == "__main__":
    main()
