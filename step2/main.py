import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.llm.openai_client import OpenAiLlmClient
from step2.indexer import Indexer
from step2.agentic_rag_chat import AgenticRagChat

def main():
    # 1. LLM Client 초기화
    client = OpenAiLlmClient()

    # 2. 인덱싱 (최초 1회, 이미 되어 있으면 스킵)
    indexer = Indexer(client)
    indexer.run_indexing()

    # 3. 챗봇 실행
    chat = AgenticRagChat(client)
    chat.start()

if __name__ == "__main__":
    main()
