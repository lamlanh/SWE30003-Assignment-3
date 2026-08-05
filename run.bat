@echo off
echo  SmartFM - Setup and Run Script (Windows)
echo.

IF NOT EXIST ".venv\" (
    echo Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

echo [1/2] Installing required libraries from requirements.txt...
pip install -r requirements.txt

echo.
echo [2/2] Starting the Streamlit application...
streamlit run app.py

pause
