#!/bin/bash

echo "  SmartFM - Setup and Run Script (Linux/Mac)"
echo ""

source .venv/bin/activate

echo "[1/2] Installing required libraries from requirements.txt..."
pip install -r requirements.txt

echo ""
echo "[2/2] Starting the Streamlit application..."
streamlit run app.py
