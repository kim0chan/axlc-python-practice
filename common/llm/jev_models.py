from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union, Any, Annotated, Literal

# --- Request DTOs ---

class JevQuestion(BaseModel):
    type: str # "choice", "noul", "score"
    instructions: str
    criteria: Optional[Union[Dict[str, str], List[str]]] = None

class JevRequest(BaseModel):
    model: str = "jev-latest"
    state: Any # String, Dict, or List
    questions: Dict[str, JevQuestion]

# --- Response DTOs ---

class JevChoiceAnswer(BaseModel):
    type: Literal["choice"] = "choice"
    choice: str
    probabilities: Dict[str, float]
    confidence: float

class JevNoulAnswer(BaseModel):
    type: Literal["noul"] = "noul"
    noul: float

class JevScoreAnswer(BaseModel):
    type: Literal["score"] = "score"
    score: float
    # API가 인덱스를 키로 하는 Dict를 줄 수도 있고, List를 줄 수도 있으므로 유연하게 대응
    probabilities: Union[Dict[str, float], List[float]]
    confidence: float

# Discriminator를 사용하여 type 필드에 따라 올바른 모델로 파싱되도록 설정
JevAnswer = Annotated[
    Union[JevChoiceAnswer, JevNoulAnswer, JevScoreAnswer],
    Field(discriminator='type')
]

class JevResponse(BaseModel):
    model: str
    answers: Dict[str, JevAnswer]
    usage: Dict[str, int]
