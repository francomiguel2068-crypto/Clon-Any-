@echo off
REM ============================================================
REM  Compilador de SARE para Windows  (doble clic para ejecutar)
REM  Genera SARE-Servidor.exe y SARE-Agente.exe en la carpeta dist\
REM  Este PC necesita internet SOLO esta vez (para bajar PyInstaller).
REM  Los .exe resultantes NO necesitan internet ni Python.
REM ============================================================
setlocal
cd /d "%~dp0\.."

echo.
echo === SARE :: Compilador de ejecutables para Windows ===
echo.

REM 1) Comprobar que Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: No se encontro Python.
    echo Instala Python 3.10 o superior desde https://www.python.org/downloads/
    echo y marca la casilla "Add Python to PATH" durante la instalacion.
    echo.
    pause
    exit /b 1
)

REM 2) Instalar PyInstaller si falta
echo Comprobando PyInstaller...
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo Instalando PyInstaller ^(requiere internet^)...
    python -m pip install --upgrade pip
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: No se pudo instalar PyInstaller. Revisa tu conexion a internet.
        pause
        exit /b 1
    )
)

REM 3) Compilar
python build\build.py
if errorlevel 1 (
    echo.
    echo ERROR durante la compilacion.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  LISTO. Los ejecutables estan en la carpeta  dist\
echo    - SARE-Servidor.exe  -^> PC del profesor
echo    - SARE-Agente.exe    -^> PCs de los estudiantes
echo      ^(junto con sare_agente.ini para indicar la IP^)
echo ============================================================
echo.
pause
