@echo off
title VeriPack - Legal Metrology Compliance Inspection System
echo ====================================================================
echo             VeriPack - Web Application Launcher
echo   Department of Consumer Affairs, Govt. of India
echo ====================================================================
echo.
echo Starting Unified Server on http://localhost:8000 ...
echo Press Ctrl+C to stop.
echo.
start http://localhost:8000
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
