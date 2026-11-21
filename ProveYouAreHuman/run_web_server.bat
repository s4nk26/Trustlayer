@echo off
title TrustLayer Web Server
echo ========================================================
echo  Starting TrustLayer Verification & Dashboard Server...
echo ========================================================
start http://localhost:8000/dashboard
start http://localhost:8000/client
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload
pause
