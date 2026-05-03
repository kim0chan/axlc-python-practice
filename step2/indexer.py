import os
import re
from common.llm.client import LlmClient
from common.llm.models import ChatMessage
from common.ui import print_info, print_success, loading_spinner, print_warning

class Indexer:
    def __init__(self, llm_client: LlmClient):
        self.llm_client = llm_client
        # 현재 파일(indexer.py)의 위치를 기준으로 프로젝트 루트 경로 계산
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.raw_dir = os.path.join(base_dir, "data", "raw")
        self.kb_dir = os.path.join(base_dir, "data", "knowledge-base")

    def run_indexing(self):
        # 1. 지식 베이스 폴더가 비어있지 않으면 건너뛰기
        if os.path.exists(self.kb_dir) and os.listdir(self.kb_dir):
            print_info("Knowledge Base가 이미 존재합니다. 인덱싱을 건너뜁니다.")
            return

        os.makedirs(self.kb_dir, exist_ok=True)
        raw_file_path = os.path.join(self.raw_dir, "axlc_lecture.txt")

        if not os.path.exists(raw_file_path):
            print_info(f"원본 파일이 없습니다: {raw_file_path}")
            return

        # 파일 내용 읽어오기
        with open(raw_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        print_info("인덱싱 시작 (LLM에게 청킹 요청 중...)")

        # 2. LLM에게 청킹 요청
        prompt = (
            "다음은 AI 응용 개발 강의 문서입니다. 이를 나중에 검색하기 좋게 '의미 있는 소주제' 단위로 쪼개주세요.\n"
            "각 조각에 대해 파일명(영어, .txt)과 내용을 다음 형식으로 출력해주세요.\n"
            "중요: 파일명에 대괄호([])나 공백을 포함하지 마세요.\n\n"
            "형식: --- FILENAME: filename.txt --- content --- END ---\n\n"
            f"문서 내용:\n{content}"
        )

        with loading_spinner("LLM이 문서를 쪼개고 있어요..."):
            response_msg = self.llm_client.ask([ChatMessage(role="user", content=prompt)])
            response_text = response_msg.content

        # 3. 정규표현식으로 파일 분리 및 저장
        pattern = re.compile(r"--- FILENAME: (.*?) ---(.*?)--- END ---", re.DOTALL)
        matches = pattern.findall(response_text)

        count = 0
        for file_name, file_content in matches:
            # 혹시 모를 대괄호나 공백 제거
            file_name = file_name.strip().replace("[", "").replace("]", "").replace(" ", "_")
            file_content = file_content.strip()

            if not file_name.endswith(".txt"):
                file_name += ".txt"

            save_path = os.path.join(self.kb_dir, file_name)
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(file_content)

            print_success(f"지식 조각 저장 완료: {file_name}")
            count += 1

        if count == 0:
            print_warning("경고: LLM 응답에서 파일을 추출하지 못했습니다!")
            print_info(f"응답 내용: {response_text}")
        else:
            print_success(f"인덱싱 완료: ({count}개 파일 생성)")
