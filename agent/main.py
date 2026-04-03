"""
Agente SARE - Prototipo Semana 1
Se conecta al servidor y ejecuta comandos recibidos.
"""
import socket
import sys
from shared.protocol import recv_message, encode, create_response

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9001

COMMAND_HANDLERS = {}


def register_command(action: str):
    """Decorador para registrar un handler de comando."""
    def decorator(func):
        COMMAND_HANDLERS[action] = func
        return func
    return decorator


@register_command("lock_screen")
def handle_lock(payload: dict) -> str:
    print("  [!] PANTALLA BLOQUEADA (simulado)")
    return "Pantalla bloqueada"


@register_command("unlock_screen")
def handle_unlock(payload: dict) -> str:
    print("  [✓] Pantalla desbloqueada (simulado)")
    return "Pantalla desbloqueada"


@register_command("ping")
def handle_ping(payload: dict) -> str:
    return "pong"


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else SERVER_HOST
    port = int(sys.argv[2]) if len(sys.argv) > 2 else SERVER_PORT

    print(f"[*] Conectando a {host}:{port}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    print("[+] Conectado al servidor")

    try:
        while True:
            msg = recv_message(sock)
            if msg is None:
                print("[-] Servidor cerró la conexión")
                break

            print(f"  <- Comando recibido: {msg['action']}")
            action = msg.get("action", "")
            handler = COMMAND_HANDLERS.get(action)

            if handler:
                result = handler(msg.get("payload", {}))
                status = "ok"
            else:
                result = f"Comando desconocido: {action}"
                status = "error"

            resp = create_response(msg["request_id"], status, result)
            sock.sendall(encode(resp))

    except (ConnectionResetError, BrokenPipeError):
        print("[-] Conexión perdida")
    finally:
        sock.close()


if __name__ == "__main__":
    main()