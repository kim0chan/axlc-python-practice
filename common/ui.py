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
        color = ConsoleColor.PURPLE
    elif role == "USER":
        color = ConsoleColor.BLUE
    else:
        color = ConsoleColor.GRAY
    
    print(f"\n{ConsoleColor.BOLD}{color}[{role}]{ConsoleColor.RESET}: {message.content}\n")

def print_info(message: str):
    print(f"{ConsoleColor.CYAN}ℹ️ {message}{ConsoleColor.RESET}")

def print_success(message: str):
    print(f"{ConsoleColor.GREEN}✅ {message}{ConsoleColor.RESET}")

def print_warning(message: str):
    print(f"{ConsoleColor.YELLOW}⚠ {message}{ConsoleColor.RESET}")

from rich.console import Console as RichConsole

# main.py 등에서 사용할 console 객체 호환용
class SimpleConsole:
    def __init__(self):
        self._rich_console = RichConsole()

    def print(self, message: Any, **kwargs):
        if isinstance(message, str):
            msg = (message
                    .replace("[bold cyan]", f"{ConsoleColor.BOLD}{ConsoleColor.CYAN}")
                    .replace("[bold magenta]", f"{ConsoleColor.BOLD}{ConsoleColor.PURPLE}")
                    .replace("[bold blue]", f"{ConsoleColor.BOLD}{ConsoleColor.BLUE}")
                    .replace("[bold yellow]", f"{ConsoleColor.BOLD}{ConsoleColor.YELLOW}")
                    .replace("[dim]", f"{ConsoleColor.GRAY}")
                    .replace("[/]", f"{ConsoleColor.RESET}"))
            print(msg)
        else:
            self._rich_console.print(message, **kwargs)

    def input(self, prompt: str) -> str:
        # 프롬프트에 색깔 입히기
        msg = prompt.replace(f"[bold blue]", f"{ConsoleColor.BOLD}{ConsoleColor.BLUE}") \
                    .replace("[/]", f"{ConsoleColor.RESET}")
        return input(msg)

    def clear(self):
        if sys.platform == "win32":
            import os
            os.system("cls")
        else:
            import os
            os.system("clear")

console = SimpleConsole()
