"""Configuración del agente: dónde está el servidor (PC del profesor).

Orden de prioridad para encontrar la IP y el puerto:
  1. Argumentos de línea de comandos:  SARE-Agente.exe 192.168.1.10 9001
  2. Archivo 'sare_agente.ini' junto al ejecutable / script
  3. Variables de entorno SARE_HOST / SARE_PORT
  4. Valores por defecto (127.0.0.1:9001)

El .ini se genera solo la primera vez para que el profesor sólo tenga que
abrirlo con el Bloc de notas y escribir la IP de su equipo.
"""
import configparser
import os
import sys

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 9001
INI_NAME = "sare_agente.ini"


def _base_dir() -> str:
    """Carpeta donde vive el ejecutable (o el script en desarrollo)."""
    if getattr(sys, "frozen", False):  # empaquetado con PyInstaller
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(sys.argv[0] or __file__))


def ini_path() -> str:
    return os.path.join(_base_dir(), INI_NAME)


def _write_default_ini(path: str, host: str, port: int):
    cfg = configparser.ConfigParser()
    cfg["servidor"] = {
        "host": host,
        "port": str(port),
        "allow_power": "false",  # apagar/reiniciar/kill desactivados por defecto
    }
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("; Configuracion del Agente SARE\n")
            f.write("; Escribe aqui la IP del PC del profesor (servidor).\n")
            f.write("; allow_power=true habilita apagar/reiniciar/cerrar sesion.\n\n")
            cfg.write(f)
    except OSError:
        pass


def load(argv=None):
    """Devuelve (host, port, allow_power)."""
    argv = sys.argv[1:] if argv is None else argv

    host = os.environ.get("SARE_HOST", DEFAULT_HOST)
    try:
        port = int(os.environ.get("SARE_PORT", DEFAULT_PORT))
    except ValueError:
        port = DEFAULT_PORT
    allow_power = os.environ.get("SARE_ALLOW_POWER", "0") == "1"

    # Archivo .ini (si existe, tiene prioridad sobre el entorno/valores default).
    path = ini_path()
    if os.path.exists(path):
        cfg = configparser.ConfigParser()
        try:
            cfg.read(path, encoding="utf-8")
            if cfg.has_section("servidor"):
                host = cfg.get("servidor", "host", fallback=host).strip() or host
                port = cfg.getint("servidor", "port", fallback=port)
                allow_power = cfg.getboolean("servidor", "allow_power", fallback=allow_power)
        except (configparser.Error, ValueError):
            pass
    else:
        # Primera ejecución: dejar un .ini de ejemplo al lado del ejecutable.
        _write_default_ini(path, host, port)

    # Argumentos de línea de comandos (máxima prioridad).
    if len(argv) >= 1 and argv[0]:
        host = argv[0]
    if len(argv) >= 2 and argv[1]:
        try:
            port = int(argv[1])
        except ValueError:
            pass

    return host, port, allow_power
