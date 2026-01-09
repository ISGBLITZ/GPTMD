@echo off

REM --- Set environment variables for AI Foundry ---
python.exe -m pip install --upgrade pip
pip install -r requirements.txt
REM --- Launch Streamlit app ---
REM --- Put wherever the location of your streamlit_app.py is ---
streamlit run _____ --server.port 8501

pause

