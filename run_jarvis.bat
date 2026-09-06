@echo off
setlocal
title Project Jarvis AI Assistant

:: 1. Auto-Locate Jarvis Project Root (Works from workspace, Desktop, or anywhere)
set "JARVIS_ROOT=%~dp0"
if not exist "%JARVIS_ROOT%main.py" (
    if exist "%USERPROFILE%\Jarvis\main.py" (
        set "JARVIS_ROOT=%USERPROFILE%\Jarvis\"
    ) else if exist "C:\Users\Krishna\Jarvis\main.py" (
        set "JARVIS_ROOT=C:\Users\Krishna\Jarvis\"
    )
)

cd /d "%JARVIS_ROOT%"

:: 2. Force UTF-8 Code Page & Unbuffered Python output
chcp 65001 >nul 2>&1
set "PYTHONUNBUFFERED=1"
set "PYTHONPATH=%JARVIS_ROOT%"

echo =================================================================
echo        PROJECT JARVIS - PERSONAL AI ASSISTANT
echo        Directory: %JARVIS_ROOT%
echo =================================================================
echo.

:: 3. Dynamic Python Runtime Resolution
set "PYTHON_EXE="
if exist "%JARVIS_ROOT%venv\Scripts\python.exe" (
    set "PYTHON_EXE=%JARVIS_ROOT%venv\Scripts\python.exe"
) else if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
) else if exist "C:\Users\Krishna\AppData\Local\Programs\Python\Python312\python.exe" (
    set "PYTHON_EXE=C:\Users\Krishna\AppData\Local\Programs\Python\Python312\python.exe"
) else (
    for /f "tokens=*" %%i in ('where python 2^>nul') do (
        if not defined PYTHON_EXE set "PYTHON_EXE=%%i"
    )
)

if not defined PYTHON_EXE set "PYTHON_EXE=python"
echo [Python] Runtime: %PYTHON_EXE%

:: 4. Fast Non-Blocking Ollama LLM Daemon Check
echo [Ollama] Verifying local LLM engine status...
powershell -NoProfile -NonInteractive -Command "$tcp = New-Object System.Net.Sockets.TcpClient; try { $res = $tcp.BeginConnect('127.0.0.1', 11434, $null, $null); if (!$res.AsyncWaitHandle.WaitOne(300, $false)) { throw } $tcp.EndConnect($res); $tcp.Close(); exit 0 } catch { if (Get-Command 'ollama' -ErrorAction SilentlyContinue) { Start-Process 'ollama' -ArgumentList 'serve' -WindowStyle Hidden } elseif (Test-Path '%LOCALAPPDATA%\Programs\Ollama\ollama.exe') { Start-Process '%LOCALAPPDATA%\Programs\Ollama\ollama.exe' -ArgumentList 'serve' -WindowStyle Hidden }; Start-Sleep -Milliseconds 800; exit 0 }" >nul 2>&1

:: 5. Launch Jarvis Engine & GUI
echo [Launch] Starting Jarvis Desktop Assistant
echo [Info]   Global Summon/Dismiss Hotkey: Ctrl + Shift + J
echo.

"%PYTHON_EXE%" "%JARVIS_ROOT%main.py" %*

set "EXIT_CODE=%ERRORLEVEL%"
if %EXIT_CODE% NEQ 0 (
    echo.
    echo =================================================================
    echo [ERROR] Jarvis exited with error code: %EXIT_CODE%
    echo =================================================================
    echo Press any key to close this terminal...
    pause >nul
) else (
    echo.
    echo [Jarvis] Session terminated cleanly.
    ping -n 3 127.0.0.1 >nul
)
