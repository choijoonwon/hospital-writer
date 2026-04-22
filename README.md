# 병원 마케팅 글쓰기 자동화

환자 정보가 담긴 Google Sheets를 연동해서, 환자별 특징(말투·수술 이력·선호도·닉네임 등)을 반영한 후기 글 초안을 AI로 자동 생성하는 웹 대시보드입니다.

생성된 글은 환자가 직접 검토 후 각 플랫폼에 게시합니다.

---

## 동작 화면

| 환자 선택 & 정보 확인 | 플랫폼·글 종류 선택 & 생성 |
|---|---|
| 환자 드롭다운 → 수술 정보·말투·닉네임 자동 표시 | 여우야/성예사/바비/강남언니 × 게시글/댓글/쪽지 선택 후 버튼 클릭 |

---

## 지원 플랫폼

| 플랫폼 | 글 스타일 |
|---|---|
| 여우야 | 감성적·친근한 톤, 언니들끼리 대화하듯 |
| 성예사 | 정보 공유 느낌, 수술 과정 상세 서술 |
| 바비 | 솔직하고 직접적, 가성비 위주 핵심 전달 |
| 강남언니 | 객관적·신뢰감, 병원/의사/회복 정보 체계적 |

글 종류: **게시글 / 댓글 / 쪽지**

---

## 설치 방법 (Windows)

### 1단계 — Python 설치
1. [python.org/downloads](https://www.python.org/downloads/) 접속
2. **Python 3.11 이상** 다운로드
3. 설치 시 **"Add Python to PATH"** 체크박스 반드시 체크

### 2단계 — 파일 받기
```
방법 A: git clone
  git clone https://github.com/choijoonwon/hospital-writer.git

방법 B: ZIP 다운로드
  GitHub 페이지 → Code → Download ZIP → 압축 해제
```

### 3단계 — 프로그램 설치
`setup.bat` 파일을 **더블클릭** 합니다.
```
자동으로 수행되는 작업:
  ✔ Python 가상환경 생성
  ✔ 필요한 패키지 설치
  ✔ .env 설정 파일 생성
```

### 4단계 — API 키 설정
`.env` 파일을 메모장으로 열어 아래 값을 입력합니다.

```env
ANTHROPIC_API_KEY=sk-ant-여기에-클로드-API-키-입력
SPREADSHEET_ID=여기에-구글시트-ID-입력
GOOGLE_CREDENTIALS_PATH=credentials.json
AI_PROVIDER=claude
```

> **Claude API 키 발급**: [console.anthropic.com](https://console.anthropic.com) → API Keys → Create Key

### 5단계 — Google Sheets 연동

> Google Cloud 서비스 계정을 만들어 스프레드시트 접근 권한을 줍니다.

1. [console.cloud.google.com](https://console.cloud.google.com) 접속
2. 새 프로젝트 생성 (이름 자유)
3. **API 및 서비스 → 라이브러리** → `Google Sheets API` 검색 → 사용 설정
4. **API 및 서비스 → 사용자 인증 정보** → 서비스 계정 만들기
5. 서비스 계정 클릭 → **키** 탭 → **키 추가 → JSON** 다운로드
6. 다운로드된 파일 이름을 `credentials.json`으로 변경 후 프로그램 폴더에 복사
7. Google Sheets 열기 → 공유 버튼 → 서비스 계정 이메일 주소 입력 → **편집자** 권한으로 공유
8. 스프레드시트 URL에서 ID 복사:
   ```
   https://docs.google.com/spreadsheets/d/[여기가 ID]/edit
   ```
   → `.env` 파일의 `SPREADSHEET_ID`에 붙여넣기

### 6단계 — 실행
`run.bat` 파일을 **더블클릭** 합니다.
→ 브라우저가 자동으로 열리며 `http://localhost:8000` 접속됩니다.

---

## 스프레드시트 컬럼 구조

시트의 **2행부터** 데이터를 읽습니다. 1행은 헤더(제목)입니다.

| 컬럼 | 내용 | 예시 |
|---|---|---|
| A | 이름 | 김민지 |
| B | 닉네임 메모 (내부용) | |
| C | 병원 알아본 날 | 11/18 |
| D | 상담 날 | 12/19 |
| E | 병원 방문 날 | 1/18 |
| F | 수술 날 | 2/18 |
| G | 수술 부위 | 윤곽 3종 |
| H | 수술 금액 | 1,350만원 |
| I | 담당 원장 | 임종우 |
| J | 연령대 말투 | 30대 초반 |
| K | 선호 키워드 | 의견반영,안전,사후관리 |
| L | 말투 스타일 | ~여 말투 |
| M | 계정 시작일 | 23년도 |
| N | 마지막 게시일 | 4월 25일 |
| O | 활동 카페 | 여우야,성위키,가아사 |
| P | 여우야 닉네임 | 싸루매 |
| Q | 성예사 닉네임 | 생각을하자 |
| R | 바비 닉네임 | 저릿저릿 |
| S | 강남언니 닉네임 | 민지2302 |
| T | 기타 닉네임 (성위키 등) | |
| U | 게시 이력 병원 | A병원,B병원 |
| V | 언급 금지 사항 | C병원 쌍수·눈교 언급 금지 |
| W | 특이사항 | |

> 컬럼 순서가 다를 경우 `backend/sheets.py` 상단의 `COLUMNS` 배열 순서를 맞춰 수정하세요.

---

## 폴더 구조

```
hospital-writer/
├── backend/
│   ├── main.py        ← 서버 (API 라우터)
│   ├── sheets.py      ← Google Sheets 연동
│   ├── generator.py   ← AI 글 생성 (Claude / GPT-4o)
│   └── prompts.py     ← 플랫폼별 프롬프트 템플릿
├── frontend/
│   ├── index.html     ← 웹 대시보드
│   ├── style.css
│   └── app.js
├── .env.example       ← 설정 파일 템플릿
├── requirements.txt   ← 패키지 목록
├── setup.bat          ← Windows 설치 스크립트
└── run.bat            ← Windows 실행 스크립트
```

---

## 자주 묻는 문제

**Q. `setup.bat` 실행 시 "Python이 설치되지 않았습니다" 오류**
→ Python 설치 시 **"Add Python to PATH"** 체크 후 재설치

**Q. 환자 목록이 안 뜰 때**
→ `credentials.json` 파일이 프로그램 폴더에 있는지 확인
→ Google Sheets에 서비스 계정 이메일이 **편집자**로 공유되어 있는지 확인
→ `.env`의 `SPREADSHEET_ID`가 정확한지 확인

**Q. 글 생성 버튼 누르면 오류**
→ `.env`의 `ANTHROPIC_API_KEY`가 올바른지 확인
→ Claude API 계정에 크레딧이 있는지 [console.anthropic.com](https://console.anthropic.com) 확인

**Q. OpenAI(ChatGPT)로 바꾸고 싶을 때**
→ `.env`에서 `AI_PROVIDER=openai` 로 변경
→ `OPENAI_API_KEY=sk-...` 추가

**Q. 창을 닫으면 프로그램이 꺼짐**
→ 정상 동작입니다. 사용할 때만 `run.bat` 실행하면 됩니다.

---

## 기술 스택

- **Backend**: Python 3.11+ / FastAPI / Uvicorn
- **Frontend**: HTML / CSS / JavaScript (설치 불필요)
- **AI**: Anthropic Claude API (기본) / OpenAI GPT-4o (선택)
- **데이터**: Google Sheets API (서비스 계정)
