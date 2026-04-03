"""
Servidor SARE - Prototipo Semana 1
Acepta conexiones de agentes y envía comandos básicos.
"""
import socket
import threading
from shared.protocol import create_message, encode, recv_message

HOST = "0.0.0.0"
PORT = 9001
agents = {}
agents_lock = threading.Lock()


def handle_agent(conn, addr):
    """Maneja la conexión con un agente individual."""
    print(f"[+] Agente conectado: {addr}")
    with agents_lock:
        agents[addr] = conn
    try:
        while True:
            msg = recv_message(conn)
            if msg is None:
                break
            print(f"    <- {addr}: {msg}")
    except (ConnectionResetError, BrokenPipeError):
        pass
    finally:
        print(f"[-] Agente desconectado: {addr}")
        with agents_lock:
            agents.pop(addr, None)
        conn.close()


def send_command(addr, action: str):
    with agents_lock:
        conn = agents.get(addr)
    if conn:
        msg = create_message(action)
        conn.sendall(encode(msg))
        print(f"    -> {addr}: {action}")
    else:
        print(f"[!] Agente {addr} no encontrado")


def console_loop():
    print("\nComandos disponibles:")
    print("  list            - Ver agentes conectados")
    print("  send <n> <cmd>  - Enviar comando (ej: send 0 lock_screen)")
    print("  quit            - Salir\n")
    while True:
        try:
            line = input("sare> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if line == "list":
            with agents_lock:
                for i, addr in enumerate(agents):
                    print(f"  [{i}] {addr}")
            if not agents:
                print("  (sin agentes conectados)")
        elif line.startswith("send "):
            parts = line.split(maxsplit=2)
            if len(parts) == 3:
                idx, action = int(parts[1]), parts[2]
                with agents_lock:
                    addrs = list(agents.keys())
                if 0 <= idx < len(addrs):
                    send_command(addrs[idx], action)
        elif line == "quit":
            break


def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(30)
    print(f"[*] Servidor SARE escuchando en {HOST}:{PORT}")

    def accept_loop():
        while True:
            conn, addr = srv.accept()
            t = threading.Thread(target=handle_agent, args=(conn, addr), daemon=True)
            t.start()

    threading.Thread(target=accept_loop, daemon=True).start()
    console_loop()
    srv.close()


if __name__ == "__main__":
    main()