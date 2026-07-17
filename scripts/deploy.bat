@echo off

echo ======================================
echo Deploy Preparation
echo ======================================

cd /d ..\backend

IF NOT EXIST venv (
    echo.
    echo Backend virtual environment not found.
    echo Create it first:
    echo python -m venv venv
    echo.
    pause
    exit /b
)

call venv\Scripts\activate

echo Installing Backend Dependencies...

pip install -r requirements.txt

echo.

cd ..\frontend

echo Installing Frontend Dependencies...

call npm install

echo.

echo Building Frontend...

call npm run build

echo.

echo Deployment preparation completed successfully.

pause