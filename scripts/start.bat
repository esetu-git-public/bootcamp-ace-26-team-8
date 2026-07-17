@echo off

echo ======================================
echo Starting Loan Default Prediction System
echo ======================================

echo Starting Backend...
start cmd /k "cd /d ..\backend && .venv\Scripts\activate && uvicorn app.main:app --reload"

timeout /t 3 > nul

echo Starting Frontend...
start cmd /k "cd /d ..\frontend && npm install && npm run dev"

echo.
echo Backend  : http://localhost:8000
echo Frontend : http://localhost:3000
echo.
pause