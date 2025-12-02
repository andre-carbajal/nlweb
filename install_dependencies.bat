@echo off
title Instalador de Dependencias NLWeb
echo ==========================================
echo    Instalando Dependencias para NLWeb
echo ==========================================
echo.

echo [1/1] Instalando librerias en 'backend'...
uv add flask flask-cors qdrant-client openai python-dotenv requests xmltodict

echo.
echo ==========================================
echo    Instalacion completada!
echo ==========================================
echo.
pause
