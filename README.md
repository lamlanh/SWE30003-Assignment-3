# SmartFM - Smart Fleet Management System

Welcome to the SmartFM application for Assignment 3! We have created automated setup scripts to make launching the app as simple as possible.

## How to Run the App

### For Windows Users
We have provided a batch script for a seamless single-click setup.
1. Open the project folder in File Explorer.
2. Double-click the `run.bat` file.
3. The script will automatically install all required dependencies and open the Streamlit application in your default web browser.

### For Linux / macOS Users
We have provided a shell script for quick deployment.
1. Open your terminal and navigate to the project directory.
2. Run the shell script by typing:
   ```bash
   ./run.sh
   ```
   *(Note: The script is already marked as executable. If you encounter permission issues, simply run `chmod +x run.sh` first).*

---

### Manual Setup (Fallback)
If you prefer not to use the automated scripts, or if you encounter any issues, you can run the application manually from your terminal:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Launch the application:**
   ```bash
   streamlit run app.py
   ```
   > **Important:** Do NOT use `python app.py` — Streamlit apps must be launched with the `streamlit run` command or the UI will not render.

Once running, the application will be accessible at: `http://localhost:8501`
