import os
import requests
from typing import List, Optional, Any
from dotenv import load_dotenv
from common.llm.client import LlmClient
from common.llm.models import ChatMessage, ChatRequest, ChatResponse

class OpenAiLlmClient(LlmClient):
    """
    OpenAI API 구현체
    표준 requests 라이브러리를 사용하여 OpenAI와 통신합니다.
    """
    
    def __init__(self, api_key: Optional[str] = None, api_url: str = "https://api.openai.com/v1/chat/completions", model_name: str = "gpt-5-nano"):
        load_dotenv()
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file or environment variables")
            
        self.api_url = api_url
        self.model_name = model_name

    def ask(self, messages: List[ChatMessage]) -> ChatMessage:
        response = self.ask_with_tools(messages)
        return response

    def ask_with_tools(self, messages: List[ChatMessage], tools: Optional[List[Any]] = None) -> ChatMessage:
        """
        Tool 목록을 포함하여 질문합니다.
        """
        try:
            # 1. 요청 객체 생성
            tool_choice = "auto" if tools else None
            chat_request = ChatRequest(
                model=self.model_name,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice
            )
            
            # Pydantic 모델을 dict로 변환 (None 값 제외)
            payload = chat_request.model_dump(exclude_none=True)
            
            # 2. HTTP Request 보내기
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = requests.post(self.api_url, json=payload, headers=headers)
            
            if response.status_code != 200:
                print(f"OpenAI API Error: {response.status_code} - {response.text}")
                return ChatMessage(role="assistant", content=f"Error: {response.status_code}")
                
            # 3. 응답 파싱
            data = response.json()
            chat_response = ChatResponse.model_validate(data)
            
            if not chat_response.choices:
                return ChatMessage(role="assistant", content="Error: No choices returned.")
                
            return chat_response.choices[0].message
            
        except Exception as e:
            print(f"Exception in OpenAiLlmClient: {e}")
            return ChatMessage(role="assistant", content=f"Exception: {str(e)}")
