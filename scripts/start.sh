#!/bin/bash

echo "======================================"
echo "Starting Loan Default Prediction System"
echo "======================================"

cd ../backend || exit
source .venv/bin/activate
uvicorn app.main:app --reload &
BACKEND_PID=$!

cd ../frontend || exit
npm install
npm run dev &
FRONTEND_PID=$!

echo ""
echo "Backend Running : http://localhost:8000"
echo "Frontend Running: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait