# AXLC Python 실습 환경 세팅 가이드

이 가이드는 AXLC Python 실습을 위한 개발 환경 구축 방법을 안내합니다.
  
---  

## 1. 준비 사항

- **Python 3.10 이상**: 최신 파이썬 기능을 활용하므로 Python 3.10 이상의 설치가 필수적입니다.
    - 추천: [Python 공식 홈페이지](https://www.python.org/downloads/)
- **Git**: 소스 코드 클론 및 버전 관리를 위해 필요합니다.
- **IDE (선택)**:
    - **PyCharm (추천)**: 파이썬 개발에 최적화된 강력한 기능을 제공합니다.
    - **VS Code**: `Python` 확장 프로그램 설치가 필요합니다.
- **Bruno (선택)**:
    - Postman과 같은 API 테스팅 툴입니다.

---  

## 2. 프로젝트 클론 및 설정

### 저장소 클론
```bash  
git clone https://github.com/kim0chan/axlc-python-practice.git
cd axlc-python-practice
```  

### 가상환경 구성 (Virtual Environment)
프로젝트의 독립된 환경을 위해 가상환경 사용을 권장합니다.

**Windows:**
```powershell  
python -m venv venv  
.\venv\Scripts\activate  
```  

**macOS/Linux:**
```bash  
python3 -m venv venvsource venv/bin/activate
```  

### 패키지 설치 (Dependencies)
```bash  
pip install -r requirements.txt
```  

### 환경 변수 설정 (.env)
실습 코드에서 OpenAI API Key를 안전하게 로드하기 위해 `.env` 파일 설정이 필요합니다.    
(실습을 위한 API Key는 크루 진행 시 전달 드리겠습니다.)
1. 프로젝트 루트에 `.env` 파일을 생성합니다.
2. 생성한 `.env` 파일을 열고 아래 내용을 입력합니다.

```env
# .env 파일 예시  
OPENAI_API_KEY=sk-proj-....  
```  
  
---  

## 3. 실행 방법

### 통합 런처를 이용한 실행
터미널에서 아래 명령어를 통해 메뉴 형식의 실습 런처를 실행할 수 있습니다.
```bash  
python main.py
```  

### 각 Step별 개별 실행
각 단계의 실습 코드를 직접 실행할 수도 있습니다.

**Windows/macOS/Linux 공통:**
> [!TIP]  
> 실습 코드 내에 ANSI 색상과 스피너가 포함되어 있습니다. 터미널의 인코딩이 UTF-8인지 확인하세요!
```bash  
# Step 0: Stateless Chat 실행  
python step0/stateless_chat.py  
  
# Step 1: Context Chat 실행  
python step1/context_chat.py  
```  
  
---  

## 4. 트러블슈팅 (Troubleshooting)

- **ModuleNotFoundError**: 실행 시 모듈을 찾을 수 없다면 `requirements.txt` 설치 여부와 가상환경 활성화 상태를 확인하세요.
- **인코딩 문제**: 한글이나 이모지가 깨져 보인다면 터미널 인코딩을 확인하세요.
    - Windows (구형 CMD): `chcp 65001` 실행 후 다시 시도
- **API 호출 실패**:
    - `.env` 파일에 API Key가 올바르게 입력되었는지 확인하세요.
    - `python-dotenv` 패키지가 정상적으로 설치되었는지 확인하세요.

---  

## 5. 특징 (Features)

- **UI**: 외부 라이브러리 의존성을 최소화하고 순수 ANSI 코드로 구현된 시각적 피드백을 제공합니다.
- **Pydantic V2**: 타입 안전성과 자동 데이터 검증을 위해 최신 Pydantic 기술을 활용합니다.
- **Minimalistic Logic**: 복잡한 추상화를 파이썬 문법으로 재구성하여 로직의 본질에 집중합니다.

---  

**즐거운 코딩 되세요!**