#!/bin/bash

echo "======================================"
echo Deploy Preparation
echo "======================================"

echo "Installing Backend Dependencies..."

cd ../backend || exit

source .venv/bin/activate

pip install -r requirements.txt

echo ""

echo "Installing Frontend Dependencies..."

cd ../frontend || exit

npm install

echo ""

echo "Building Frontend..."

npm run build

echo ""
echo "Deployment preparation completed successfully."