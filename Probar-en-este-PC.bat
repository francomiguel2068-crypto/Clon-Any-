@echo off
chcp 65001 >nul
cd /d "%~dp0"
title SARE - Prueba en este PC
REM Abre el servidor y un agente en el MISMO PC, para comprobar que todo
REM funciona antes de probar entre dos computadores. Doble clic y listo.

echo ============================================================
echo  SARE - Prueba rapida en este mismo PC
echo ============================================================
echo.

REM 1) Abrir el servidor en su propia ventana
echo Abriendo el servidor...
if exist "SARE-Servidor.exe" (
    start "SARE Servidor" "SARE-Servidor.exe"
) else (
    where py >nul 2>&1 && ( start "SARE Servidor" py run_server.py ) || ( start "SARE Servidor" python run_server.py )
)

REM 2) Esperar unos segundos a que el servidor abra
echo Esperando a que abra el servidor...
timeout /t 3 /nobreak >nul

REM 3) Abrir un agente conectado a este mismo PC (127.0.0.1)
echo Abriendo un agente conectado a este PC...
echo.
if exist "SARE-Agente.exe" (
    "SARE-Agente.exe" 127.0.0.1 9001
) else (
    where py >nul 2>&1 && ( py run_agent.py 127.0.0.1 9001 ) || ( python run_agent.py 127.0.0.1 9001 )
)

echo.
echo Si cerraste el agente, esta ventana se puede cerrar.
pause
