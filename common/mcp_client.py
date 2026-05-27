import json
import subprocess
import threading
import sys
from typing import Any, Dict, List, Optional

class McpClient:
    """
    개별 MCP 서버와의 연결을 관리하는 클라이언트
    stdio 기반의 JSON-RPC 통신을 사용하여 특정 MCP 서버와 대화
    """

    def __init__(self, name: str, command: List[str]):
        self.name = name # 식별을 위한 이름 추가
        self.command = command
        self.process: Optional[subprocess.Popen] = None
        self.id_counter = 1
        self._lock = threading.Lock()
        
        # 서버 시작
        self._start_server()
        # Handshake
        self.initialize()

    def _start_server(self):
        """MCP 서버 프로세스를 실행"""
        # Windows에서는 npx가 .cmd 파일이므로 shell=True가 필요할 수 있음
        self.process = subprocess.Popen(
            self.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, # stderr 버퍼가 차서 데드락이 발생하는 것을 방지
            text=True,
            encoding="utf-8", # UTF-8 인코딩 명시 (Windows 한글 환경 대응)
            bufsize=1,
            shell=(sys.platform == "win32")
        )

    def initialize(self):
        """서버 초기화 과정 진행"""
        params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "resources": {},
                "tools": {}
            },
            "clientInfo": {
                "name": "AXLC-Python-Client",
                "version": "1.0.0"
            }
        }
        
        response = self.send_request("initialize", params)
        if "error" in response:
            raise Exception(f"MCP 서버 초기화 실패: {response['error']}")
        
        # 초기화 완료 알림 발송
        self.send_notification("notifications/initialized", {})

    def get_tools(self) -> List[Dict[str, Any]]:
        """서버에서 사용 가능한 도구 목록 가져오기"""
        response = self.send_request("tools/list", {})
        if "result" in response and "tools" in response["result"]:
            return response["result"]["tools"]
        return []

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """서버의 특정 도구 호출"""
        params = {
            "name": name,
            "arguments": arguments
        }
        
        response = self.send_request("tools/call", params)
        if "result" in response and "content" in response["result"]:
            content_list = response["result"]["content"]
            texts = [item.get("text", "") for item in content_list if item.get("type") == "text"]
            return "\n".join(texts)
        elif "error" in response:
            return f"ERROR: {response['error']}"
        
        return "ERROR: Tool execution failed"

    def send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """JSON-RPC 요청을 보내고 응답 대기"""
        with self._lock:
            req_id = self.id_counter
            self.id_counter += 1
            
            request = {
                "jsonrpc": "2.0",
                "id": req_id,
                "method": method,
                "params": params
            }
            
            # 요청 전송
            json_str = json.dumps(request)
            self.process.stdin.write(json_str + "\n")
            self.process.stdin.flush()
            
            # 응답 수신 (매칭되는 ID가 나올 때까지 읽음)
            while True:
                line = self.process.stdout.readline()
                if not line:
                    raise Exception("MCP 서버로부터 응답을 읽을 수 없습니다.")
                
                try:
                    resp = json.loads(line)
                    if resp.get("id") == req_id:
                        return resp
                except json.JSONDecodeError:
                    # JSON이 아닌 로그 메시지 등은 무시
                    continue

    def send_notification(self, method: str, params: Dict[str, Any]):
        """JSON-RPC 알림(Notification) 전송"""
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
        json_str = json.dumps(notification)
        self.process.stdin.write(json_str + "\n")
        self.process.stdin.flush()

    def close(self):
        """프로세스를 안전하게 종료"""
        if self.process:
            self.process.terminate()
            self.process.wait()

class MultiMcpManager:
    """
    여러 개의 MCP 서버 연결을 통합 관리하는 매니저
    """
    def __init__(self):
        self.clients: List[McpClient] = []

    def add_server(self, name: str, command: List[str]):
        """새로운 MCP 서버 연결 추가"""
        client = McpClient(name, command)
        self.clients.append(client)
        return client

    def get_all_tools(self) -> List[tuple[McpClient, Dict[str, Any]]]:
        """모든 서버로부터 사용 가능한 도구 목록 취합 (클라이언트 정보 포함)"""
        all_tools = []
        for client in self.clients:
            tools = client.get_tools()
            for tool in tools:
                all_tools.append((client, tool))
        return all_tools

    def close_all(self):
        """모든 MCP 서버 연결 종료"""
        for client in self.clients:
            client.close()
