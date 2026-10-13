"""Implementación de los comandos que ejecuta el agente.

Filosofía:
  - En Windows se ejecutan de verdad las acciones SEGURAS de gestión de aula
    (bloquear pantalla, mensaje, abrir URL, info, listar procesos).
  - En otros sistemas (macOS/Linux) y para los comandos de ENERGÍA se devuelve
    una respuesta simulada, para poder desarrollar y probar sin tumbar máquinas.
  - Los comandos de energía (apagar, reiniciar, cerrar sesión, matar proceso)
    sólo se ejecutan de verdad si se habilitan explícitamente con set_power(True)
    o con la variable de entorno SARE_ALLOW_POWER=1. Por defecto están apagados.

Todo es con librería estándar de Python: no se descarga nada en los equipos.
"""
import os
import platform
import subprocess
import threading
import webbrowser

IS_WINDOWS = platform.system() == "Windows"

# ¿Se permiten los comandos de energía de verdad? Por defecto NO.
_ALLOW_POWER = os.environ.get("SARE_ALLOW_POWER", "0") == "1"

COMMAND_HANDLERS = {}


def set_power(enabled: bool):
    """Habilita o deshabilita la ejecución real de comandos de energía."""
    global _ALLOW_POWER
    _ALLOW_POWER = bool(enabled)


def power_enabled() -> bool:
    return _ALLOW_POWER


def register(action: str):
    def deco(func):
        COMMAND_HANDLERS[action] = func
        return func
    return deco


def dispatch(action: str, payload: dict):
    """Ejecuta un comando y devuelve (status, message)."""
    handler = COMMAND_HANDLERS.get(action)
    if not handler:
        return "error", f"Comando desconocido: {action}"
    try:
        return "ok", handler(payload or {})
    except Exception as e:  # nunca dejar caer el agente por un comando
        return "error", f"Error en '{action}': {e}"


# --------------------------------------------------------------------------- #
# Comandos SEGUROS (se ejecutan de verdad en Windows)
# --------------------------------------------------------------------------- #
@register("ping")
def _ping(payload):
    return "pong"


@register("sysinfo")
def _sysinfo(payload):
    u = platform.uname()
    return (
        f"OS={u.system} {u.release} | Host={u.node} | "
        f"Arch={u.machine} | Python={platform.python_version()}"
    )


@register("lock_screen")
def _lock(payload):
    if IS_WINDOWS:
        import ctypes
        ctypes.windll.user32.LockWorkStation()
        return "Pantalla bloqueada"
    return "Pantalla bloqueada (simulado: no es Windows)"


@register("unlock_screen")
def _unlock(payload):
    # Por seguridad del sistema operativo, desbloquear requiere la contraseña
    # del usuario; no se puede (ni se debe) hacer por software remoto.
    return "El desbloqueo lo hace el usuario con su contraseña"


@register("show_msg")
def _show_msg(payload):
    text = str(payload.get("text", "")).strip()
    if not text:
        return "Error: falta 'text' en el payload"
    if IS_WINDOWS:
        import ctypes
        # MB_OK | MB_ICONINFORMATION | MB_SYSTEMMODAL, en un hilo para no bloquear.
        def _box():
            ctypes.windll.user32.MessageBoxW(0, text, "Mensaje del profesor", 0x40 | 0x1000)
        threading.Thread(target=_box, daemon=True).start()
        return f"Mensaje mostrado: {text}"
    return f"Mensaje mostrado (simulado): {text}"


@register("open_url")
def _open_url(payload):
    url = str(payload.get("url", "")).strip()
    if not url:
        return "Error: falta 'url' en el payload"
    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url
    webbrowser.open(url)
    return f"URL abierta: {url}"


@register("list_procs")
def _list_procs(payload):
    system = platform.system()
    if system == "Windows":
        cmd = ["tasklist", "/FO", "CSV", "/NH"]
    elif system == "Linux":
        cmd = ["ps", "aux", "--no-header"]
    else:
        cmd = ["ps", "-eo", "pid,comm"]
    out = subprocess.check_output(cmd, text=True, timeout=5)
    lines = [l for l in out.strip().splitlines() if l][:20]
    return "\n".join(lines) if lines else "(sin procesos)"


@register("screenshot")
def _screenshot(payload):
    # El streaming/captura real queda como trabajo futuro: requeriría una
    # librería externa (Pillow) y rompería la promesa de "sin descargar nada".
    return "Captura de pantalla (demo) — el streaming real queda pendiente"


# --------------------------------------------------------------------------- #
# Comandos de ENERGÍA / peligrosos (apagados por defecto)
# --------------------------------------------------------------------------- #
def _power_action(name, win_cmd, posix_cmd=None):
    if not _ALLOW_POWER:
        return f"{name}: deshabilitado (simulado). Actívalo con SARE_ALLOW_POWER=1"
    if IS_WINDOWS:
        subprocess.Popen(win_cmd)
        return f"{name}: ejecutado"
    if posix_cmd:
        subprocess.Popen(posix_cmd)
        return f"{name}: ejecutado"
    return f"{name}: no soportado en este sistema (simulado)"


@register("shutdown")
def _shutdown(payload):
    return _power_action("Apagar", ["shutdown", "/s", "/t", "0"])


@register("restart")
def _restart(payload):
    return _power_action("Reiniciar", ["shutdown", "/r", "/t", "0"])


@register("logout")
def _logout(payload):
    return _power_action("Cerrar sesión", ["shutdown", "/l"])


@register("kill_proc")
def _kill_proc(payload):
    pid = payload.get("pid")
    if pid in (None, ""):
        return "Error: falta 'pid' en el payload"
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return f"Error: pid inválido ({pid!r})"
    if not _ALLOW_POWER:
        return f"Matar PID {pid}: deshabilitado (simulado). Actívalo con SARE_ALLOW_POWER=1"
    if IS_WINDOWS:
        subprocess.Popen(["taskkill", "/PID", str(pid), "/F"])
    else:
        os.kill(pid, 9)
    return f"Proceso {pid} terminado"
