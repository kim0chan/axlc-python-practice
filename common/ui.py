import sys
import time
import threading
from typing import Any
from contextlib import contextmanager

from common.llm.models import ChatMessage


# 1. ANSI 색상 상수
class ConsoleColor:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    
    # 기본 색상
    BLUE = "\033[34m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    RED = "\033[31m"
    PURPLE = "\033[35m"
    GRAY = "\033[90m"

    @staticmethod
    def init():
        if sys.platform == "win32":
            import os
            os.system("")

ConsoleColor.init()

# 2. 테마 정의 (UI 일관성을 위해 추가)
class Theme:
    HEADER = f"{ConsoleColor.BOLD}{ConsoleColor.CYAN}"
    USER = f"{ConsoleColor.BOLD}{ConsoleColor.BLUE}"
    ASSISTANT = f"{ConsoleColor.BOLD}{ConsoleColor.PURPLE}"
    SYSTEM = f"{ConsoleColor.GRAY}"
    INFO = f"{ConsoleColor.CYAN}"
    SUCCESS = f"{ConsoleColor.GREEN}"
    WARNING = f"{ConsoleColor.YELLOW}"
    ERROR = f"{ConsoleColor.RED}"
    RESET = ConsoleColor.RESET

class SpinnerThread(threading.Thread):
    def __init__(self, message: str):
        super().__init__(daemon=True)
        self.message = message
        self.stop_event = threading.Event()
        self.chars = ["|", "/", "-", "\\"]

    def run(self):
        idx = 0
        while not self.stop_event.is_set():
            sys.stdout.write(f"\r{ConsoleColor.YELLOW}{self.chars[idx % 4]} {self.message}{ConsoleColor.RESET}")
            sys.stdout.flush()
            idx += 1
            time.sleep(0.1)

        sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")
        sys.stdout.flush()

@contextmanager
def loading_spinner(message: str = "LLM은 생각 중..."):
    spinner = SpinnerThread(message)
    spinner.start()
    try:
        yield
    finally:
        spinner.stop_event.set()
        spinner.join()

def print_message(message: ChatMessage):
    """
    역할에 따라 ANSI 코드를 입혀서 출력
    """
    role = message.role.upper()

    if role == "ASSISTANT":
        style = Theme.ASSISTANT
    elif role == "USER":
        style = Theme.USER
    else:
        style = Theme.SYSTEM
    
    print(f"\n{style}[{role}]{Theme.RESET}: {message.content}\n")

def print_info(message: str):
    print(f"{Theme.INFO}ℹ️ {message}{Theme.RESET}")

def print_success(message: str):
    print(f"{Theme.SUCCESS}✅ {message}{Theme.RESET}")

def print_warning(message: str):
    print(f"{Theme.WARNING}⚠ {message}{Theme.RESET}")

def print_error(message: str):
    print(f"{Theme.ERROR}❌ {message}{Theme.RESET}")

from rich.console import Console as RichConsole

# main.py 등에서 사용할 console 객체 호환용
class SimpleConsole:
    def __init__(self):
        self._rich_console = RichConsole()

    def print(self, message: Any, style: str = None, **kwargs):
        if isinstance(message, str):
            if style:
                print(f"{style}{message}{Theme.RESET}")
            else:
                # 하위 호환성을 위해 기본적인 rich 태그만 일부 지원하되, 점진적으로 제거 권장
                msg = (message
                        .replace("[bold cyan]", Theme.HEADER)
                        .replace("[bold magenta]", Theme.ASSISTANT)
                        .replace("[bold blue]", Theme.USER)
                        .replace("[bold yellow]", Theme.WARNING)
                        .replace("[dim]", Theme.SYSTEM)
                        .replace("[/]", Theme.RESET))
                print(msg)
        else:
            self._rich_console.print(message, **kwargs)

    def print_header(self, message: str):
        self.print(f"\n{Theme.HEADER}=== {message} ==={Theme.RESET}\n")

    def input(self, prompt: str, style: str = Theme.USER) -> str:
        # 프롬프트에 스타일 입히기
        return input(f"{style}{prompt}{Theme.RESET}")

    def clear(self):
        if sys.platform == "win32":
            import os
            os.system("cls")
        else:
            import os
            os.system("clear")

console = SimpleConsole()
