import os
import requests
from typing import Dict, Any, Union, List
from dotenv import load_dotenv
from common.llm.jev_models import JevRequest, JevResponse, JevQuestion

load_dotenv()

class JevClient:
    """
    TypeSafe AI Jev (System One) Model Client
    """
    def __init__(self, api_key: str = None, base_url: str = "https://api.typesafe.ai/v1"):
        self.api_key = api_key or os.getenv("JEV_API_KEY")
        self.base_url = base_url
        self.endpoint = f"{self.base_url}/systemone"
        
        if not self.api_key:
            raise ValueError("JEV_API_KEY is not set. Please provide it in .env file or constructor.")

    def decide(self, state: Any, questions: Dict[str, JevQuestion], model: str = "jev-latest") -> JevResponse:
        """
        Jev 모델에게 판단(Decision)을 요청합니다.
        """
        request_data = JevRequest(
            model=model,
            state=state,
            questions=questions
        )

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        response = requests.post(
            self.endpoint,
            headers=headers,
            json=request_data.model_dump(exclude_none=True)
        )

        if response.status_code != 200:
            raise Exception(f"Jev API Error ({response.status_code}): {response.text}")

        return JevResponse.model_validate(response.json())

    # 편의 메서드들
    def choice(self, state: Any, instructions: str, criteria: Dict[str, str], model: str = "jev-latest") -> str:
        """단일 Choice 질문을 던지고 선택된 결과를 반환합니다."""
        questions = {
            "q1": JevQuestion(type="choice", instructions=instructions, criteria=criteria)
        }
        res = self.decide(state, questions, model)
        return res.answers["q1"].choice

    def noul(self, state: Any, instructions: str, model: str = "jev-latest") -> float:
        """단일 Noul 질문을 던지고 확률값을 반환합니다."""
        questions = {
            "q1": JevQuestion(type="noul", instructions=instructions)
        }
        res = self.decide(state, questions, model)
        return res.answers["q1"].noul

    def score(self, state: Any, instructions: str, criteria: List[str], model: str = "jev-latest") -> float:
        """단일 Score 질문을 던지고 점수를 반환합니다."""
        questions = {
            "q1": JevQuestion(type="score", instructions=instructions, criteria=criteria)
        }
        res = self.decide(state, questions, model)
        return res.answers["q1"].score
