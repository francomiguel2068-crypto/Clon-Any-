"""Consola de texto (CLI) del servidor SARE.

Usa ServerCore para la red y shared.ui para el estilo de la terminal.
Para la versión con ventana gráfica, ver server/gui.py.
"""
import json
import os

from server.core import ServerCore, HOST, PORT
from shared.ui import (
    BANNER_SERVER, RESET, BOLD, DIM,
    BRIGHT_CYAN, BRIGHT_GREEN, BRIGHT_RED, BRIGHT_YELLOW,
    BRIGHT_WHITE, BRIGHT_MAGENTA, BRIGHT_BLACK,
    success, error, warn, info, arrow_right, arrow_left,
    hr, print_help_server, print_agent_table,
)

_LEVEL_FMT = {
    "info": info,
    "ok": success,
    "error": error,
    "warn": warn,
}


def _on_connect(agent_id, addr):
    label = f"{addr[0]}:{addr[1]}"
    print(success(f"Agente {BRIGHT_YELLOW}#{agent_id}{RESET} conectado: {BRIGHT_CYAN}{label}{RESET}"))


def _on_disconnect(agent_id, addr):
    label = f"{addr[0]}:{addr[1]}"
    print(warn(f"Agente {BRIGHT_YELLOW}#{agent_id}{RESET} desconectado: {BRIGHT_CYAN}{label}{RESET}"))


def _on_message(agent_id, addr, status, message, raw):
    label = f"{addr[0]}:{addr[1]}"
    if status == "ok":
        print(arrow_left(
            f"{BRIGHT_YELLOW}#{agent_id}{RESET} {DIM}{label}{RESET}  "
            f"{BRIGHT_GREEN}●{RESET} {BRIGHT_WHITE}{message}{RESET}"
        ))
    elif status == "error":
        print(arrow_left(
            f"{BRIGHT_YELLOW}#{agent_id}{RESET} {DIM}{label}{RESET}  "
            f"{BRIGHT_RED}●{RESET} {BRIGHT_RED}{message}{RESET}"
        ))
    else:
        print(arrow_left(f"{BRIGHT_YELLOW}#{agent_id}{RESET} {DIM}{label}{RESET}  {raw}"))


def _on_sent(agent_id, addr, action, payload):
    label = f"{addr[0]}:{addr[1]}"
    extra = f"  {DIM}{json.dumps(payload)}{RESET}" if payload else ""
    print(arrow_right(
        f"{BRIGHT_YELLOW}#{agent_id}{RESET} {DIM}{label}{RESET}  "
        f"{BRIGHT_MAGENTA}▸{RESET} {BRIGHT_WHITE}{action}{RESET}{extra}"
    ))


def _on_log(level, text):
    fmt = _LEVEL_FMT.get(level, info)
    print(fmt(text))


def console_loop(server: ServerCore):
    print_help_server()
    prompt = f"  {BRIGHT_GREEN}{BOLD}sare{RESET}{BRIGHT_BLACK} ❯{RESET} "

    while True:
        try:
            line = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{info('Cerrando servidor...')}")
            break

        if not line:
            continue

        if line == "list":
            print_agent_table(server.snapshot())

        elif line.startswith("sendp "):
            parts = line.split(maxsplit=3)
            if len(parts) >= 4:
                try:
                    aid = int(parts[1])
                    action = parts[2]
                    payload = json.loads(parts[3])
                except (ValueError, json.JSONDecodeError) as e:
                    print(error(f"Error parseando: {BRIGHT_YELLOW}{e}{RESET}"))
                    continue
                server.send_command(aid, action, payload)
            else:
                print(error(f"Uso: {BRIGHT_CYAN}sendp <id> <cmd> <json>{RESET}"))

        elif line.startswith("send "):
            parts = line.split(maxsplit=2)
            if len(parts) == 3:
                try:
                    aid, action = int(parts[1]), parts[2]
                except ValueError:
                    print(error(f"Uso: {BRIGHT_CYAN}send <id> <comando>{RESET}"))
                    continue
                server.send_command(aid, action)
            else:
                print(error(f"Uso: {BRIGHT_CYAN}send <id> <comando>{RESET}"))

        elif line.startswith("broadcast "):
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                server.broadcast(parts[1])
            else:
                print(error(f"Uso: {BRIGHT_CYAN}broadcast <comando>{RESET}"))

        elif line.startswith("kick "):
            parts = line.split()
            if len(parts) == 2:
                try:
                    aid = int(parts[1])
                except ValueError:
                    print(error(f"Uso: {BRIGHT_CYAN}kick <id>{RESET}"))
                    continue
                if server.kick(aid):
                    print(info(f"Agente {BRIGHT_YELLOW}#{aid}{RESET} desconectado"))
            else:
                print(error(f"Uso: {BRIGHT_CYAN}kick <id>{RESET}"))

        elif line == "clear":
            os.system("cls" if os.name == "nt" else "clear")
            print(BANNER_SERVER)

        elif line == "help":
            print_help_server()

        elif line == "quit":
            print(info("Cerrando servidor..."))
            break

        else:
            print(error(f"Comando desconocido: {BRIGHT_YELLOW}{line}{RESET}  — escribe {BRIGHT_CYAN}help{RESET}"))


def main():
    print(BANNER_SERVER)

    server = ServerCore(HOST, PORT)
    server.on_connect = _on_connect
    server.on_disconnect = _on_disconnect
    server.on_message = _on_message
    server.on_sent = _on_sent
    server.on_log = _on_log

    try:
        server.start()
    except OSError as e:
        print(error(f"No se pudo abrir el servidor en el puerto {PORT}: {e}"))
        return

    print(f"  {hr('─', BRIGHT_BLACK)}")
    console_loop(server)
    server.stop()


if __name__ == "__main__":
    main()
