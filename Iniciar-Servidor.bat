@echo off
chcp 65001 >nul
cd /d "%~dp0"
title SARE - Servidor (PC del profesor)
REM Doble clic en el PC del PROFESOR. Abre la consola del servidor y muestra
REM la IP de este PC, que es la que hay que escribir en el agente del otro PC.

echo ============================================================
echo  SARE - Servidor (este es el PC del profesor)
echo ============================================================
echo.
echo  IP de este PC en la red local (escribela en el otro PC):
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do echo        %%a
echo.
echo  (Si no aparece ninguna, conecta este PC al Wi-Fi o cable de red.)
echo ============================================================
echo.
echo  Abriendo la consola del servidor...

if exist "SARE-Servidor.exe" (
    start "SARE Servidor" "SARE-Servidor.exe"
) else (
    where py >nul 2>&1 && ( start "SARE Servidor" py run_server.py ) || ( start "SARE Servidor" python run_server.py )
)
