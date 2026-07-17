#!/bin/bash

echo "======================================"
echo "Starting Loan Default Prediction System"
echo "======================================"

cd ../backend || exit

if [ ! -d "venv" ]; then
    echo ""
    echo "Backend virtual environment not found."
    echo ""
    echo "Run these commands once:"
    echo ""
    echo "python3 -m venv venv"
    echo "source venv/bin/activate"
    echo "pip install -r requirements.txt"
    exit 1
fi

source venv/bin/activate

uvicorn app.main:app --reload &
BACKEND_PID=$!

cd ../frontend || exit

if [ ! -d "node_modules" ]; then
    npm install
fi

npm run dev &
FRONTEND_PID=$!

echo ""
echo "Backend Running : http://localhost:8000"
echo "Frontend Running: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

wait