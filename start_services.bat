@echo off
title NLWeb Launcher
echo ==========================================
echo    Iniciando NLWeb en Windows Server
echo ==========================================
echo.

:: 1. Iniciar Servidor Unificado (Backend + Frontend)
echo [1/1] Iniciando Servidor NLWeb (Puerto 8000)...
start "NLWeb Server" cmd /k "uv run python server.py"

:: Esperar un poco para que el backend arranque
timeout /t 3 /nobreak >nul

echo.
echo ==========================================
echo    Todo listo!
echo    Accede a la web en: http://localhost:8000
echo    (O usa tu IP local para acceder desde otros dispositivos)
echo ==========================================
echo.
pause
