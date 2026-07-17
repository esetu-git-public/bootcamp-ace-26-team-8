#!/bin/bash

echo "======================================"
echo "Deploy Preparation"
echo "======================================"

cd ../backend || exit

if [ ! -d "venv" ]; then
    echo ""
    echo "Backend virtual environment not found."
    echo ""
    echo "Run:"
    echo "python3 -m venv venv"
    echo "source venv/bin/activate"
    echo "pip install -r requirements.txt"
    exit 1
fi

source venv/bin/activate

echo "Installing Backend Dependencies..."

pip install -r requirements.txt

echo ""

cd ../frontend || exit

echo "Installing Frontend Dependencies..."

npm install

echo ""

echo "Building Frontend..."

npm run build

echo ""
echo "Deployment preparation completed successfully."