@echo off
chcp 65001 >nul
cd /d "%~dp0"
title SARE - Agente (PC del estudiante)
REM Doble clic en cada PC de ESTUDIANTE. Pregunta la IP del PC del profesor
REM y conecta este equipo a ese servidor.

echo ============================================================
echo  SARE - Agente (este PC se conectara al profesor)
echo ============================================================
echo.
echo  En el PC del profesor abre "Iniciar-Servidor.bat"; ahi te muestra
echo  su IP (algo como 192.168.x.x). Escribela aqui abajo.
echo.
set /p ip=IP del PC del profesor (Enter = este mismo PC):
if "%ip%"=="" set ip=127.0.0.1

echo.
echo  Conectando a %ip% ...
echo.
if exist "SARE-Agente.exe" (
    "SARE-Agente.exe" %ip% 9001
) else (
    where py >nul 2>&1 && ( py run_agent.py %ip% 9001 ) || ( python run_agent.py %ip% 9001 )
)

echo.
pause
