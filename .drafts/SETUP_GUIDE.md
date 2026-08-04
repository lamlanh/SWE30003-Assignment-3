# Developer Setup Guide

Because we are using a Virtual Environment (`.venv`) to isolate our Python packages, you must set up your local environment before you can run the SmartFM application. 

The `.venv` folder is ignored by Git to save space, meaning **every team member must run these steps on their own computer** after cloning the repository.

---

## Linux / macOS (Bash/Zsh)

1. **Create the virtual environment:**
   ```bash
   python3 -m venv .venv
   ```

2. **Activate the environment:**
   ```bash
   source .venv/bin/activate
   ```
   *(You should see `(.venv)` appear at the start of your terminal prompt)*

3. **Install the project dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```

---

## Windows (PowerShell)

1. **Create the virtual environment:**
   ```powershell
   python -m venv .venv
   ```

2. **Activate the environment:**
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
   *(Note: If Windows throws a red text permissions error, open PowerShell as Administrator and run `Set-ExecutionPolicy Unrestricted -Scope CurrentUser`, then try activating again)*

3. **Install the project dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```powershell
   streamlit run app.py
   ```

---

## How to exit the environment
When you are done coding for the day, you can turn off the virtual environment on any operating system by simply typing:
```bash
deactivate
```
