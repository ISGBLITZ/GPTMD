@echo off
REM --- Activate virtual environment ---
call "C:\Users\Ishaa\OneDrive\Iwanthealth\IwantHealth_venv\Scripts\activate.bat"

REM --- Set environment variables for AI Foundry ---
python.exe -m pip install --upgrade pip
pip install -r requirements.txt
REM --- Launch Streamlit app ---
streamlit run "C:\Users\Ishaa\OneDrive\Iwanthealth\streamlit_app.py" --server.port 8501

pause
