@echo off
chcp 65001 >nul
echo ===================================
echo  병원 마케팅 글쓰기 자동화 - 설치
echo ===================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되지 않았습니다.
    echo https://www.python.org/downloads/ 에서 Python 3.11 이상을 설치한 뒤 다시 실행하세요.
    pause
    exit /b 1
)

echo [1/3] Python 가상환경 생성 중...
python -m venv venv
if errorlevel 1 (
    echo [오류] 가상환경 생성 실패
    pause
    exit /b 1
)

echo [2/3] 패키지 설치 중... (시간이 걸릴 수 있습니다)
venv\Scripts\pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [오류] 패키지 설치 실패
    pause
    exit /b 1
)

echo [3/3] 설정 파일 초기화...
if not exist .env (
    copy .env.example .env >nul
    echo .env 파일이 생성되었습니다.
)

echo.
echo ===================================
echo  설치 완료!
echo ===================================
echo.
echo 다음 단계:
echo   1. .env 파일을 메모장으로 열어 API 키 입력
echo   2. credentials.json 파일을 이 폴더에 복사
echo   3. run.bat 실행
echo.
pause
