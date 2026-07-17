@echo off

echo ======================================
echo Deploy Preparation
echo ======================================

echo Installing Backend Dependencies...

cd ..\backend

call .venv\Scripts\activate

pip install -r requirements.txt

echo.

echo Installing Frontend Dependencies...

cd ..\frontend

call npm install

echo.

echo Building Frontend...

call npm run build

echo.

echo Deployment preparation completed successfully.

pause