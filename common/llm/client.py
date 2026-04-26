from abc import ABC, abstractmethod
from typing import List
from common.llm.models import ChatMessage

class LlmClient(ABC):
    """
    LLM Client Common Interface
    """
    
    @abstractmethod
    def ask(self, messages: List[ChatMessage]) -> ChatMessage:
        """
        대화 메시지 목록을 보내고, LLM의 응답(텍스트)을 반환합니다.
        """
        pass
