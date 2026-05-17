import sys
import os
import importlib
import traceback

# 프로젝트 루트를 path에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from common.ui import console, ConsoleColor

def show_menu():
    title = "AXLC Practice"
    padding = " " * 4
    line = "━" * (len(title) + 8)

    print(f"\n{ConsoleColor.BOLD}{ConsoleColor.PURPLE}{line}")
    print(f"┃{padding}{title}{padding}┃")
    print(f"{line}{ConsoleColor.RESET}")
    print(f"{ConsoleColor.GRAY} 원하는 실습 단계를 선택해주세요.{ConsoleColor.RESET}\n")
    
    steps = {
        "0": ("Step 0: Stateless Chat (첫 API 호출)", "step0.stateless_chat"),
        "1": ("Step 1: Context Chat (대화 맥락 관리)", "step1.context_chat"),
        "2": ("Step 2: Agentic RAG (지식 기반 대화)", "step2.main"),
        "3": ("Step 3: Primitive Agent (원시 에이전트)", "step3.primitive_agent"),
        "4": ("Step 4: Tool Call Agent (도구를 사용하는 에이전트)", "step4.tool_call_agent"),
        "q": ("종료하기", None)
    }

    for key, (desc, _) in steps.items():
        print(f"  {ConsoleColor.BOLD}{ConsoleColor.CYAN}{key}{ConsoleColor.RESET}: {desc}")

    # 입력 받기
    choice = input(f"\n{ConsoleColor.BOLD}{ConsoleColor.YELLOW} 선택 (기본: q): {ConsoleColor.RESET}").strip().lower()
    if not choice: choice = "q"
    
    return steps.get(choice)

def main():
    while True:
        choice_info = show_menu()
        if not choice_info or choice_info[1] is None:
            print(f"\n{ConsoleColor.YELLOW}고생하셨습니다.{ConsoleColor.RESET}")
            break
        
        module_path = choice_info[1]
        try:
            print(f"\n{ConsoleColor.BOLD}{ConsoleColor.GREEN}>>> {choice_info[0]} 실행 중...{ConsoleColor.RESET}\n")
            
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
                print(f"{ConsoleColor.RED}에러: {module_path} 모듈에 main() 함수가 없습니다.{ConsoleColor.RESET}")
                
            print(f"\n{ConsoleColor.BOLD}{ConsoleColor.GREEN}--- 실습 완료 ---{ConsoleColor.RESET}\n")
            input("엔터를 누르면 메뉴로 돌아갑니다...")
            console.clear()
            
        except Exception as e:
            print(f"\n{ConsoleColor.BOLD}{ConsoleColor.RED}실행 중 오류 발생:{ConsoleColor.RESET} {str(e)}")
            traceback.print_exc()
            input("\n엔터를 누르면 메뉴로 돌아갑니다...")
            console.clear()

if __name__ == "__main__":
    main()
