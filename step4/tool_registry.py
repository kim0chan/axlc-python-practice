import inspect
import json
from typing import Any, Callable, Dict, List, Optional, Type
from pydantic import BaseModel

class Tool:
    """
    AI(OpenAI GPT)가 사용할 수 있는 도구의 규격
    """
    def get_name(self) -> str: pass
    def get_description(self) -> str: pass
    def get_parameters_schema(self) -> Dict[str, Any]: pass
    def execute(self, arguments: Dict[str, Any]) -> Any: pass

class McpTool(Tool):
    """
    MCP 서버에서 제공하는 도구를 래핑한 구현체
    """
    def __init__(self, client: Any, name: str, description: str, input_schema: Dict[str, Any]):
        self.client = client
        self.name = name
        self.description = description
        self.input_schema = input_schema

    def get_name(self) -> str:
        return self.name

    def get_description(self) -> str:
        return self.description

    def get_parameters_schema(self) -> Dict[str, Any]:
        return self.input_schema

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.client.call_tool(self.name, arguments)

class FunctionalTool(Tool):
    """
    함수(Callable)를 기반으로 자동 스키마 생성을 지원하는 도구 구현체
    """
    def __init__(self, func: Callable, name: str, description: str):
        self.func = func
        self.name = name
        self.description = description
        
        # 함수의 첫 번째 파라미터 타입을 가져와서 Pydantic 모델인지 확인
        sig = inspect.signature(func)
        params = list(sig.parameters.values())
        if not params:
            raise ValueError(f"Function {func.__name__} must have at least one parameter.")
        
        self.args_class: Type[BaseModel] = params[0].annotation
        if not issubclass(self.args_class, BaseModel):
            raise ValueError(f"The first parameter of {func.__name__} must be a Pydantic BaseModel.")

    def get_name(self) -> str:
        return self.name

    def get_description(self) -> str:
        return self.description

    def get_parameters_schema(self) -> Dict[str, Any]:
        # Pydantic v2의 model_json_schema()를 사용해서 스키마 추출
        schema = self.args_class.model_json_schema()
        
        # OpenAI 규격에 맞게 조금 다듬기 (title 같은 필드는 필요 없으니)
        if "title" in schema: del schema["title"]
        return schema

    def execute(self, arguments: Dict[str, Any]) -> Any:
        try:
            # 전달받은 dict(JSON)를 Pydantic 모델로 변환해서 함수에 넘겨주기
            args_obj = self.args_class.model_validate(arguments)
            return self.func(args_obj)
        except Exception as e:
            return f"Error executing tool: {str(e)}"

class ToolRegistry:
    """
    도구 관리자 (Tool Registry)
    """
    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        print(f"[ToolRegistry] Registering tool: {tool.get_name()}")
        self.tools[tool.get_name()] = tool

    def get(self, name: str) -> Optional[Tool]:
        return self.tools.get(name)

    def get_tool_specifications(self) -> List[Dict[str, Any]]:
        """
        LLM 요청에 포함할 도구 명세 리스트(OpenAI 규격)를 반환
        """
        specs = []
        for tool in self.tools.values():
            spec = {
                "type": "function",
                "function": {
                    "name": tool.get_name(),
                    "description": tool.get_description(),
                    "parameters": tool.get_parameters_schema()
                }
            }
            specs.append(spec)
        return specs

    def handle_tool_call(self, tool_call) -> str:
        """
        LLM의 Tool Call 요청을 처리하고 결과를 반환
        """
        tool = self.get(tool_call.function.name)
        if not tool:
            return f"Error: Tool not found - {tool_call.function.name}"

        try:
            # OpenAI는 arguments를 JSON 문자열로 준다.
            args = json.loads(tool_call.function.arguments)
            result = tool.execute(args)
            return str(result) if result is not None else "Success (No return value)"
        except Exception as e:
            return f"Error executing tool: {str(e)}"
