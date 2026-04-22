@echo off
chcp 65001 >nul
echo ===================================
echo  병원 마케팅 글쓰기 자동화 - 시작
echo ===================================
echo.

if not exist venv (
    echo [오류] 설치가 되지 않았습니다. setup.bat을 먼저 실행하세요.
    pause
    exit /b 1
)

if not exist .env (
    echo [오류] .env 파일이 없습니다. setup.bat을 실행하고 API 키를 입력하세요.
    pause
    exit /b 1
)

if not exist credentials.json (
    echo [경고] credentials.json 파일이 없습니다.
    echo Google Sheets 연동이 안 될 수 있습니다.
    echo.
)

echo 서버를 시작합니다...
echo 브라우저에서 http://localhost:8000 으로 접속하세요.
echo 종료하려면 이 창을 닫으세요.
echo.

start "" http://localhost:8000
venv\Scripts\uvicorn backend.main:app --host 0.0.0.0 --port 8000

pause
