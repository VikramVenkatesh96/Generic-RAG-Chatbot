@echo off
title FAQ Chatbot Demo Controller

echo ===============================
echo Starting FAQ Chatbot Demo
echo ===============================

REM Activate virtual environment
call Chatbot\Scripts\activate

REM Start backend in new window and give it a custom title
start "FAQ_BACKEND" cmd /k "cd backend && uvicorn Chatbot:app --host 127.0.0.1 --port 8000"

REM Wait until backend is responding
echo Waiting for backend to be ready...

:waitloop
curl -s http://127.0.0.1:8000 >nul 2>&1
if errorlevel 1 (
    timeout /t 1 >nul
    goto waitloop
)

echo Backend ready.

REM Start frontend server
start "FAQ_FRONTEND" cmd /k "cd frontend && python -m http.server 5500"

timeout /t 2 >nul

REM Open browser
start http://127.0.0.1:5500

echo.
echo Demo running.
echo Close the BACKEND window to shut everything down.
echo.

REM Monitor backend window
:monitor
tasklist /v | findstr "FAQ_BACKEND" >nul
if errorlevel 1 (
    echo Backend closed. Shutting down frontend...
    taskkill /FI "WINDOWTITLE eq FAQ_FRONTEND" /F >nul 2>&1
    exit
)

timeout /t 2 >nul
goto monitor
