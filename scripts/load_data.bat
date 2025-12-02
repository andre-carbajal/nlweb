@echo off
title Cargador de Datos NLWeb
echo ==========================================
echo    Cargando Datos en Qdrant
echo ==========================================
echo.

echo [1/1] Ejecutando script de carga...
uv run python cargar_datos.py

echo.
echo ==========================================
echo    Carga finalizada!
echo ==========================================
echo.
pause
