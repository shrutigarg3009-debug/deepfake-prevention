@echo off
title PulseShield - Proactive Biometric Video Cloaking
echo =====================================================================
echo  PulseShield: Proactive Biometric Video Cloaking
echo  AI-Powered Facial Identity Protection & rPPG Desynchronization
echo =====================================================================
echo.
echo Starting Streamlit Web Application on http://localhost:8501 ...
echo.
cd /d "%~dp0"
"C:\Users\LENOVO\AppData\Local\Programs\Python\Python311\Scripts\streamlit.exe" run app.py --server.port=8501 --browser.gatherUsageStats=false
pause
