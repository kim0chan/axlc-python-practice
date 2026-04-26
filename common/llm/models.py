from typing import List, Optional, Any
from pydantic import BaseModel

class FunctionCall(BaseModel):
    name: str
    arguments: str  # JSON String

class ToolCall(BaseModel):
    id: str
    type: str = "function"
    function: FunctionCall

class ChatMessage(BaseModel):
    role: str
    content: Optional[str] = None
    name: Optional[str] = None  # Tool 이름 (role이 tool일 때)
    tool_call_id: Optional[str] = None  # Tool 실행 ID (role이 tool일 때)
    tool_calls: Optional[List[ToolCall]] = None  # Assistant가 Tool 사용을 요청할 때

class ChatRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    tools: Optional[List[Any]] = None
    tool_choice: Optional[str] = None

class Choice(BaseModel):
    message: ChatMessage

class ChatResponse(BaseModel):
    choices: List[Choice]
