@echo off

echo ======================================
echo Starting Loan Default Prediction System
echo ======================================

cd /d ..\backend

IF NOT EXIST venv (
    echo.
    echo ======================================
    echo Backend virtual environment not found.
    echo.
    echo Run the following commands once:
    echo.
    echo python -m venv venv
    echo venv\Scripts\activate
    echo pip install -r requirements.txt
    echo.
    pause
    exit /b
)

echo Starting Backend...
start cmd /k "cd /d %CD% && call venv\Scripts\activate && uvicorn app.main:app --reload"

timeout /t 3 > nul

cd ..\frontend

IF NOT EXIST node_modules (
    echo Installing Frontend Dependencies...
    call npm install
)

echo Starting Frontend...
start cmd /k "cd /d %CD% && npm run dev"

echo.
echo Backend  : http://localhost:8000
echo Frontend : http://localhost:3000
echo.
pause