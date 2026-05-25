import os
from common.llm.client import LlmClient
from common.llm.models import ChatMessage
from common.ui import console, print_message, print_info, loading_spinner, Theme

class AgenticRagChat:
    def __init__(self, llm_client: LlmClient):
        self.llm_client = llm_client
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.kb_dir = os.path.join(base_dir, "data", "knowledge-base")
        self.history = [
            ChatMessage(role="system", content="너는 AI 응용 개발 전문 튜터야. 지식 베이스의 내용을 바탕으로 답변해줘.")
        ]

    def start(self):
        console.print_header("Agentic RAG Chatbot 시작 (exit 입력 시 종료)")

        while True:
            # 1. 사용자 입력 받기
            user_input = console.input("[User]: ")
            if user_input.lower() == "exit":
                print_info("대화를 종료합니다. Bye!")
                break

            # 2. 어떤 문서를 읽을지 결정
            selected_file = self._select_document(user_input)
            context = ""

            if selected_file != "NONE" and os.path.exists(os.path.join(self.kb_dir, selected_file)):
                console.print(f">>> 지식 탐색 중... [{selected_file}] 파일을 읽습니다.", style=Theme.INFO)
                with open(os.path.join(self.kb_dir, selected_file), "r", encoding="utf-8") as f:
                    context = f.read()
            else:
                console.print(">>> 관련 지식을 찾지 못했습니다. 일반 답변을 생성합니다.", style=Theme.WARNING)

            # 3. Generator: 문맥 주입 후 답변 생성
            if context:
                final_prompt = f"다음 문맥을 참고하여, 내용에 충실하게 답변해줘.\n\n[문맥]\n{context}\n\n[질문]\n{user_input}"
            else:
                final_prompt = user_input

            self.history.append(ChatMessage(role="user", content=final_prompt))

            with loading_spinner("답변을 생성하고 있어요..."):
                response_msg = self.llm_client.ask(self.history)

            print_message(response_msg)
            self.history.append(response_msg)

    def _select_document(self, query: str) -> str:
        """
        사용자 질문에 적합한 지식 베이스 파일을 선택합니다.
        """
        if not os.path.exists(self.kb_dir):
            return "NONE"

        file_names = [f for f in os.listdir(self.kb_dir) if os.path.isfile(os.path.join(self.kb_dir, f))]
        if not file_names:
            return "NONE"

        prompt = (
            "다음은 지식 베이스에 있는 파일 목록입니다:\n" + str(file_names) + "\n\n" +
            "사용자의 질문 [" + query + "]에 답하기 위해 읽어야 할 파일 하나를 골라주세요.\n" +
            "관련 있는 파일이 없다면 'NONE'이라고만 답하세요.\n" +
            "파일이 있다면 파일명만 출력하세요. (예: pricing.txt)"
        )

        # 주의: 히스토리 없이 단발성 질문(Stateless)으로 처리
        with loading_spinner("적절한 지식을 찾는 중..."):
            response_msg = self.llm_client.ask([ChatMessage(role="user", content=prompt)])
        
        selected = response_msg.content.strip()
        # 불필요한 따옴표나 마크다운 서식 제거
        selected = selected.replace("'", "").replace('"', "").replace("`", "")

        # 실제로 파일이 존재하는지 검증
        if selected in file_names:
            return selected

        for f_name in file_names:
            if selected == f_name or selected in f_name:
                return f_name
        
        return "NONE"
