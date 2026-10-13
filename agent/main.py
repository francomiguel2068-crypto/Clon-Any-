"""Agente SARE (cliente de aula).

Se conecta al servidor del profesor, espera comandos y los ejecuta mediante
agent.actions. Si el servidor no está disponible, reintenta cada pocos segundos
(reconexión automática), ideal para encender los equipos del aula en cualquier
orden.

Uso:
    python -m agent.main [IP_SERVIDOR] [PUERTO]
    SARE-Agente.exe 192.168.1.10 9001
"""
import socket
import time

from agent import actions, config
from shared.protocol import recv_message, encode, create_response
from shared.ui import (
    BANNER_AGENT, RESET, BOLD, DIM,
    BRIGHT_CYAN, BRIGHT_GREEN, BRIGHT_RED, BRIGHT_WHITE,
    BRIGHT_YELLOW, success, error, warn, info, arrow_left, hr,
)

RECONNECT_DELAY = 5  # segundos entre intentos de reconexión


def _serve(sock):
    """Atiende comandos en una conexión ya establecida."""
    while True:
        msg = recv_message(sock)
        if msg is None:
            print(f"\n{warn('Servidor cerró la conexión')}")
            return

        action = msg.get("action", "")
        print(arrow_left(f"Comando recibido: {BRIGHT_WHITE}{BOLD}{action}{RESET}"))

        status, result = actions.dispatch(action, msg.get("payload", {}))

        resp = create_response(msg.get("request_id", ""), status, result)
        try:
            sock.sendall(encode(resp))
        except OSError:
            print(f"\n{error('No se pudo responder; conexión perdida')}")
            return

        color = BRIGHT_GREEN if status == "ok" else BRIGHT_RED
        print(f"    {DIM}{result}{RESET}")
        print(f"    {DIM}respuesta:{RESET} {color}{status}{RESET}\n")


def _connect_once(host, port):
    """Un intento de conexión. Devuelve el socket conectado o None."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        return sock
    except (ConnectionRefusedError, OSError):
        sock.close()
        return None


def main():
    host, port, allow_power = config.load()
    actions.set_power(allow_power)

    print(BANNER_AGENT)
    power_txt = f"{BRIGHT_GREEN}activados{RESET}" if allow_power else f"{DIM}desactivados{RESET}"
    print(info(f"Servidor objetivo: {BRIGHT_CYAN}{host}{RESET}:{BRIGHT_GREEN}{port}{RESET}"))
    print(info(f"Comandos de energía: {power_txt}  {DIM}(editable en {config.INI_NAME}){RESET}"))
    print(info(f"Comandos: {BRIGHT_WHITE}{', '.join(actions.COMMAND_HANDLERS)}{RESET}"))
    print(f"  {hr('─')}")

    waiting_notified = False
    try:
        while True:
            sock = _connect_once(host, port)
            if sock is None:
                if not waiting_notified:
                    print(warn(
                        f"No hay servidor en {BRIGHT_CYAN}{host}:{port}{RESET} — "
                        f"esperando a que se abra {DIM}(reintento cada {RECONNECT_DELAY}s, "
                        f"Ctrl+C para salir){RESET}"
                    ))
                    waiting_notified = True
                time.sleep(RECONNECT_DELAY)
                continue

            waiting_notified = False
            print(success(f"Conectado al servidor {BRIGHT_CYAN}{host}:{port}{RESET}"))
            print(info(f"Esperando comandos...  {DIM}(Ctrl+C para salir){RESET}\n"))
            try:
                _serve(sock)
            except (ConnectionResetError, BrokenPipeError):
                print(f"\n{error('Conexión perdida')}")
            finally:
                try:
                    sock.close()
                except OSError:
                    pass
            print(info(f"Reintentando conexión en {RECONNECT_DELAY}s...\n"))
            time.sleep(RECONNECT_DELAY)

    except KeyboardInterrupt:
        print(f"\n{info('Agente detenido por el usuario')}")


if __name__ == "__main__":
    main()
