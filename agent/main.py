import os
import socket
import sys
import platform
import subprocess
from shared.protocol import recv_message, encode, create_response
from shared.ui import (
    BANNER_AGENT, RESET, BOLD, DIM,
    BRIGHT_CYAN, BRIGHT_GREEN, BRIGHT_RED, BRIGHT_YELLOW,
    BRIGHT_WHITE, BRIGHT_MAGENTA, BRIGHT_BLUE,
    success, error, warn, info, arrow_left, hr,
)

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9001

COMMAND_HANDLERS = {}


def register_command(action: str):
    def decorator(func):
        COMMAND_HANDLERS[action] = func
        return func
    return decorator


@register_command("lock_screen")
def handle_lock(payload: dict) -> str:
    print(f"    {BRIGHT_RED}{BOLD}🔒 PANTALLA BLOQUEADA{RESET}  {DIM}(simulado){RESET}")
    return "Pantalla bloqueada"


@register_command("unlock_screen")
def handle_unlock(payload: dict) -> str:
    print(f"    {BRIGHT_GREEN}{BOLD}🔓 PANTALLA DESBLOQUEADA{RESET}  {DIM}(simulado){RESET}")
    return "Pantalla desbloqueada"


@register_command("ping")
def handle_ping(payload: dict) -> str:
    print(f"    {BRIGHT_CYAN}🏓 pong{RESET}")
    return "pong"


@register_command("screenshot")
def handle_screenshot(payload: dict) -> str:
    print(f"    {BRIGHT_MAGENTA}📸 CAPTURA DE PANTALLA{RESET}  {DIM}(simulado){RESET}")
    return "Captura realizada (simulado) — se enviaría por UDP en producción"


@register_command("sysinfo")
def handle_sysinfo(payload: dict) -> str:
    uname = platform.uname()
    info_text = (
        f"OS={uname.system} {uname.release} | "
        f"Host={uname.node} | "
        f"Arch={uname.machine} | "
        f"Python={platform.python_version()}"
    )
    print(f"    {BRIGHT_BLUE}💻 {info_text}{RESET}")
    return info_text


@register_command("list_procs")
def handle_list_procs(payload: dict) -> str:
    print(f"    {BRIGHT_CYAN}📋 LISTANDO PROCESOS{RESET}")
    try:
        if platform.system() == "Windows":
            out = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True, timeout=5)
        else:
            out = subprocess.check_output(["ps", "aux", "--no-header"] if platform.system() == "Linux" else ["ps", "-eo", "pid,comm"], text=True, timeout=5)
        lines = out.strip().split("\n")[:20]
        result = "\n".join(lines)
        print(f"    {DIM}({len(lines)} procesos mostrados){RESET}")
        return result
    except Exception as e:
        return f"Error listando procesos: {e}"


@register_command("kill_proc")
def handle_kill_proc(payload: dict) -> str:
    pid = payload.get("pid")
    if not pid:
        print(f"    {BRIGHT_YELLOW}⚠ Falta el campo 'pid' en payload{RESET}")
        return "Error: falta pid en payload"
    print(f"    {BRIGHT_RED}💀 KILL PROCESO PID={pid}{RESET}  {DIM}(simulado){RESET}")
    return f"Proceso {pid} terminado (simulado)"


@register_command("open_url")
def handle_open_url(payload: dict) -> str:
    url = payload.get("url", "")
    if not url:
        print(f"    {BRIGHT_YELLOW}⚠ Falta el campo 'url' en payload{RESET}")
        return "Error: falta url en payload"
    print(f"    {BRIGHT_BLUE}🌐 ABRIENDO URL: {BRIGHT_WHITE}{url}{RESET}  {DIM}(simulado){RESET}")
    return f"URL abierta: {url} (simulado)"


@register_command("show_msg")
def handle_show_msg(payload: dict) -> str:
    text = payload.get("text", "")
    if not text:
        print(f"    {BRIGHT_YELLOW}⚠ Falta el campo 'text' en payload{RESET}")
        return "Error: falta text en payload"
    print(f"    {BRIGHT_GREEN}💬 MENSAJE EMERGENTE:{RESET} {BRIGHT_WHITE}{text}{RESET}  {DIM}(simulado){RESET}")
    return f"Mensaje mostrado: {text} (simulado)"


@register_command("shutdown")
def handle_shutdown(payload: dict) -> str:
    print(f"    {BRIGHT_RED}{BOLD}⏻  APAGANDO EQUIPO{RESET}  {DIM}(simulado){RESET}")
    return "Equipo apagándose (simulado)"


@register_command("restart")
def handle_restart(payload: dict) -> str:
    print(f"    {BRIGHT_YELLOW}{BOLD}🔄 REINICIANDO EQUIPO{RESET}  {DIM}(simulado){RESET}")
    return "Equipo reiniciándose (simulado)"


@register_command("logout")
def handle_logout(payload: dict) -> str:
    print(f"    {BRIGHT_MAGENTA}{BOLD}🚪 CERRANDO SESIÓN{RESET}  {DIM}(simulado){RESET}")
    return "Sesión cerrada (simulado)"


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else SERVER_HOST
    port = int(sys.argv[2]) if len(sys.argv) > 2 else SERVER_PORT

    print(BANNER_AGENT)
    print(info(f"Conectando a {BRIGHT_CYAN}{host}{RESET}:{BRIGHT_GREEN}{port}{RESET}..."))

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
    except ConnectionRefusedError:
        print(error(f"No se pudo conectar a {BRIGHT_CYAN}{host}:{port}{RESET}"))
        print(f"    {DIM}¿Está el servidor corriendo?{RESET}")
        return

    print(success(f"Conectado al servidor {BRIGHT_CYAN}{host}:{port}{RESET}"))
    print(f"  {hr('─')}")
    cmds = ", ".join(COMMAND_HANDLERS.keys())
    print(info(f"Comandos registrados: {BRIGHT_WHITE}{cmds}{RESET}"))
    print(info(f"Esperando comandos...  {DIM}(Ctrl+C para salir){RESET}"))
    print()

    try:
        while True:
            msg = recv_message(sock)
            if msg is None:
                print(f"\n{warn('Servidor cerró la conexión')}")
                break

            action = msg.get("action", "")
            print(arrow_left(f"Comando recibido: {BRIGHT_WHITE}{BOLD}{action}{RESET}"))

            handler = COMMAND_HANDLERS.get(action)

            if handler:
                result = handler(msg.get("payload", {}))
                status = "ok"
            else:
                result = f"Comando desconocido: {action}"
                status = "error"
                print(f"    {BRIGHT_YELLOW}? comando no registrado{RESET}")

            resp = create_response(msg["request_id"], status, result)
            sock.sendall(encode(resp))

            status_color = BRIGHT_GREEN if status == "ok" else BRIGHT_RED
            print(f"    {DIM}respuesta enviada:{RESET} {status_color}{status}{RESET}\n")

    except (ConnectionResetError, BrokenPipeError):
        print(f"\n{error('Conexión perdida')}")
    except KeyboardInterrupt:
        print(f"\n{info('Desconectando...')}")
    finally:
        sock.close()
        print(info("Agente detenido"))


if __name__ == "__main__":
    main()
