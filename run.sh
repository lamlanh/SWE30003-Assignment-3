#!/bin/bash

echo "  SmartFM - Setup and Run Script (Linux/Mac)"
echo ""

if [ ! -d ".venv" ]; then                                                                             
    echo "Creating virtual environment..."                                                            
    python3 -m venv .venv                                                                             
fi  

source .venv/bin/activate

echo "[1/2] Installing required libraries from requirements.txt..."
pip install -r requirements.txt

echo ""
echo "[2/2] Starting the Streamlit application..."
streamlit run app.py
