"""Compila SARE a ejecutables independientes con PyInstaller.

Genera dos .exe de un solo archivo que NO necesitan Python ni internet en el
equipo de destino:
    - SARE-Servidor.exe   (consola del profesor, con interfaz gráfica)
    - SARE-Agente.exe     (cliente que va en cada PC del aula)

Uso (desde la raíz del proyecto, en el PC que SÍ tiene internet):
    python build/build.py

Requisitos del equipo que compila:  Python 3.10+ y PyInstaller
    pip install pyinstaller

Nota: PyInstaller produce ejecutables para el MISMO sistema donde se compila.
Para obtener .exe de Windows hay que compilar en Windows.
"""
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
BUILD = os.path.join(ROOT, "build", "_pyinstaller")


def _check_pyinstaller():
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("ERROR: PyInstaller no está instalado.")
        print("Instálalo con:  pip install pyinstaller")
        sys.exit(1)


def _run(name, entry, windowed):
    print(f"\n=== Compilando {name} ===")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean", "--onefile",
        "--name", name,
        "--distpath", DIST,
        "--workpath", BUILD,
        "--specpath", BUILD,
        "--windowed" if windowed else "--console",
        "--paths", ROOT,
        os.path.join(ROOT, entry),
    ]
    subprocess.check_call(cmd, cwd=ROOT)


def _write_sample_ini():
    ini = os.path.join(DIST, "sare_agente.ini")
    with open(ini, "w", encoding="utf-8") as f:
        f.write("; Configuracion del Agente SARE\n")
        f.write("; Pon aqui la IP del PC del profesor (servidor) y guarda.\n")
        f.write("; allow_power=true habilita apagar/reiniciar/cerrar sesion.\n\n")
        f.write("[servidor]\n")
        f.write("host = 192.168.1.10\n")
        f.write("port = 9001\n")
        f.write("allow_power = false\n")
    print(f"  Creado ejemplo de configuración: {ini}")


def main():
    _check_pyinstaller()
    os.makedirs(DIST, exist_ok=True)

    # Servidor: con ventana (sin consola negra detrás).
    _run("SARE-Servidor", "run_server.py", windowed=True)
    # Agente: con consola, para que se vean los comandos recibidos (útil en clase).
    _run("SARE-Agente", "run_agent.py", windowed=False)

    _write_sample_ini()

    print("\n========================================")
    print(" Compilación terminada.")
    print(f" Ejecutables en: {DIST}")
    print(" Copia a cada PC del aula:")
    print("   - SARE-Servidor.exe  -> PC del profesor")
    print("   - SARE-Agente.exe + sare_agente.ini -> PCs de los estudiantes")
    print("========================================")


if __name__ == "__main__":
    main()
