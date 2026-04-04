import json
import os
import socket
import threading
from shared.protocol import create_message, encode, recv_message
from shared.ui import (
    BANNER_SERVER, RESET, BOLD, DIM,
    BRIGHT_CYAN, BRIGHT_GREEN, BRIGHT_RED, BRIGHT_YELLOW,
    BRIGHT_WHITE, BRIGHT_MAGENTA, BRIGHT_BLACK,
    success, error, warn, info, arrow_right, arrow_left,
    hr, print_help_server, print_agent_table,
)

HOST = "0.0.0.0"
PORT = 9001
agents = {}
agents_lock = threading.Lock()
next_agent_id = 0


def handle_agent(conn, addr, agent_id):
    label = f"{addr[0]}:{addr[1]}"
    print(success(f"Agente {BRIGHT_YELLOW}#{agent_id}{RESET} conectado: {BRIGHT_CYAN}{label}{RESET}"))
    with agents_lock:
        agents[agent_id] = {"conn": conn, "addr": addr}
    try:
        while True:
            msg = recv_message(conn)
            if msg is None:
                break
            status = msg.get("status", "")
            message = msg.get("message", "")
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
                print(arrow_left(
                    f"{BRIGHT_YELLOW}#{agent_id}{RESET} {DIM}{label}{RESET}  {msg}"
                ))
    except (ConnectionResetError, BrokenPipeError, OSError):
        pass
    finally:
        print(warn(f"Agente {BRIGHT_YELLOW}#{agent_id}{RESET} desconectado: {BRIGHT_CYAN}{label}{RESET}"))
        with agents_lock:
            agents.pop(agent_id, None)
        try:
            conn.close()
        except OSError:
            pass


def get_agent(agent_id: int):
    with agents_lock:
        return agents.get(agent_id)


def send_command(agent_id: int, action: str, payload: dict = None):
    entry = get_agent(agent_id)
    if entry:
        conn = entry["conn"]
        addr = entry["addr"]
        label = f"{addr[0]}:{addr[1]}"
        msg = create_message(action, payload)
        conn.sendall(encode(msg))
        extra = f"  {DIM}{json.dumps(payload)}{RESET}" if payload else ""
        print(arrow_right(
            f"{BRIGHT_YELLOW}#{agent_id}{RESET} {DIM}{label}{RESET}  "
            f"{BRIGHT_MAGENTA}▸{RESET} {BRIGHT_WHITE}{action}{RESET}{extra}"
        ))
    else:
        print(error(f"Agente {BRIGHT_YELLOW}#{agent_id}{RESET} no encontrado"))


def broadcast_command(action: str, payload: dict = None):
    with agents_lock:
        ids = list(agents.keys())
    if not ids:
        print(warn("No hay agentes conectados"))
        return
    for aid in ids:
        send_command(aid, action, payload)
    print(info(f"Comando {BRIGHT_WHITE}{action}{RESET} enviado a {BRIGHT_CYAN}{len(ids)}{RESET} agente(s)"))


def kick_agent(agent_id: int):
    entry = get_agent(agent_id)
    if entry:
        addr = entry["addr"]
        try:
            entry["conn"].close()
        except OSError:
            pass
        print(info(f"Agente {BRIGHT_YELLOW}#{agent_id}{RESET} {BRIGHT_CYAN}{addr[0]}:{addr[1]}{RESET} desconectado"))
    else:
        print(error(f"Agente {BRIGHT_YELLOW}#{agent_id}{RESET} no encontrado"))


def console_loop():
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
            with agents_lock:
                snapshot = dict(agents)
            print_agent_table(snapshot)

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
                send_command(aid, action, payload)
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
                send_command(aid, action)
            else:
                print(error(f"Uso: {BRIGHT_CYAN}send <id> <comando>{RESET}"))

        elif line.startswith("broadcast "):
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                broadcast_command(parts[1])
            else:
                print(error(f"Uso: {BRIGHT_CYAN}broadcast <comando>{RESET}"))

        elif line.startswith("kick "):
            parts = line.split()
            if len(parts) == 2:
                try:
                    kick_agent(int(parts[1]))
                except ValueError:
                    print(error(f"Uso: {BRIGHT_CYAN}kick <id>{RESET}"))
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
    global next_agent_id
    print(BANNER_SERVER)

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(30)

    print(info(
        f"Servidor escuchando en "
        f"{BRIGHT_CYAN}{HOST}{RESET}:{BRIGHT_GREEN}{PORT}{RESET}"
    ))
    print(f"  {hr('─', BRIGHT_BLACK)}")

    def accept_loop():
        global next_agent_id
        while True:
            conn, addr = srv.accept()
            with agents_lock:
                agent_id = next_agent_id
                next_agent_id += 1
            t = threading.Thread(target=handle_agent, args=(conn, addr, agent_id), daemon=True)
            t.start()

    threading.Thread(target=accept_loop, daemon=True).start()
    console_loop()
    srv.close()


if __name__ == "__main__":
    main()
