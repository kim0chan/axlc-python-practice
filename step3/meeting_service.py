import time
from typing import Dict, List
from pydantic import BaseModel, Field

# DTO 정의 (Pydantic)
class CreateMeetingRequest(BaseModel):
    date: str = Field(description="날짜 (YYYY-MM-DD)")
    time: str = Field(description="시간 (HH:mm)")
    attendees: str = Field(description="참석자 명단")

class UpdateMeetingRequest(BaseModel):
    id: int = Field(description="수정할 예약의 고유 ID (예약 번호)")
    date: str = Field(description="변경할 날짜 (YYYY-MM-DD)")
    time: str = Field(description="변경할 시간 (HH:mm)")
    attendees: str = Field(description="변경할 참석자 명단")

class DeleteMeetingRequest(BaseModel):
    id: int = Field(description="취소할 예약의 고유 ID (예약 번호)")

class MeetingService:
    """
    가상의 미팅 예약 시스템 (In-memory DB)
    """
    def __init__(self):
        self.meeting_database: Dict[int, str] = {}
        self.id_generator = int(time.time())

    def create_meeting(self, req: CreateMeetingRequest) -> str:
        if self._is_duplicate(req.date, req.time):
            return f"ERROR: {req.date} {req.time} 시각은 이미 예약되어 있습니다. 다른 시간을 선택해 주세요."

        self.id_generator += 1
        new_id = self.id_generator
        details = f"[ID: {new_id}] {req.date} {req.time} (참석자: {req.attendees})"
        self.meeting_database[new_id] = details
        return f"SUCCESS: 예약이 확정되었습니다. (예약번호: {new_id})"

    def update_meeting(self, req: UpdateMeetingRequest) -> str:
        if req.id not in self.meeting_database:
            return f"ERROR: 해당 예약 번호({req.id})를 찾을 수 없습니다."

        if self._is_duplicate_excluding(req.date, req.time, req.id):
            return f"ERROR: {req.date} {req.time} 시각은 이미 다른 예약이 잡혀 있습니다."

        details = f"[ID: {req.id}] {req.date} {req.time} (참석자: {req.attendees}) [수정됨]"
        self.meeting_database[req.id] = details
        return "SUCCESS: 예약이 성공적으로 수정되었습니다."

    def delete_meeting(self, req: DeleteMeetingRequest) -> str:
        if req.id in self.meeting_database:
            del self.meeting_database[req.id]
            return f"SUCCESS: 예약 번호 {req.id}번이 취소되었습니다."
        return f"ERROR: 해당 예약 번호({req.id})가 존재하지 않습니다."

    def get_meeting_list(self, _=None) -> str:
        meetings = self.find_all_meetings()
        if not meetings:
            return "현재 예약된 미팅이 없습니다."
        return "\n".join(meetings)

    def find_all_meetings(self) -> List[str]:
        return list(self.meeting_database.values())

    def _is_duplicate(self, date: str, time: str) -> bool:
        target = f"{date} {time}"
        return any(target in details for details in self.meeting_database.values())

    def _is_duplicate_excluding(self, date: str, time: str, meeting_id: int) -> bool:
        target = f"{date} {time}"
        return any(target in details for id, details in self.meeting_database.items() if id != meeting_id)
