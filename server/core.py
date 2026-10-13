"""Núcleo de red del servidor SARE.

Contiene toda la lógica de sockets y gestión de agentes, sin imprimir nada.
La consola (CLI) y la interfaz gráfica (GUI) se construyen encima de esta clase
pasando funciones callback para enterarse de los eventos.
"""
import socket
import threading

from shared.protocol import create_message, encode, recv_message

HOST = "0.0.0.0"
PORT = 9001


class ServerCore:
    """Servidor TCP que acepta agentes y les envía comandos.

    Eventos (callbacks opcionales, todos reciben datos ya listos para mostrar):
      - on_connect(agent_id, addr)
      - on_disconnect(agent_id, addr)
      - on_message(agent_id, addr, status, message, raw)
      - on_log(level, text)          level: "info" | "ok" | "error" | "warn"
      - on_sent(agent_id, addr, action, payload)
    """

    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self._srv = None
        self._agents = {}
        self._lock = threading.Lock()
        self._next_id = 0
        self._running = False

        # Callbacks (se asignan desde la CLI o la GUI).
        self.on_connect = None
        self.on_disconnect = None
        self.on_message = None
        self.on_log = None
        self.on_sent = None

    # ---- utilidades internas -------------------------------------------------
    def _emit(self, cb, *args):
        if cb:
            try:
                cb(*args)
            except Exception:
                # Nunca dejar que un error de la UI tumbe el hilo de red.
                pass

    def _log(self, level, text):
        self._emit(self.on_log, level, text)

    # ---- ciclo de vida -------------------------------------------------------
    def start(self):
        """Abre el socket y arranca el hilo que acepta conexiones."""
        if self._running:
            return
        self._srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._srv.bind((self.host, self.port))
        self._srv.listen(30)
        self._running = True
        self._log("info", f"Servidor escuchando en {self.host}:{self.port}")
        threading.Thread(target=self._accept_loop, daemon=True).start()

    def stop(self):
        """Cierra todas las conexiones y el socket de escucha."""
        self._running = False
        with self._lock:
            agents = list(self._agents.values())
            self._agents.clear()
        for entry in agents:
            try:
                entry["conn"].close()
            except OSError:
                pass
        if self._srv:
            try:
                self._srv.close()
            except OSError:
                pass
            self._srv = None

    def _accept_loop(self):
        while self._running:
            try:
                conn, addr = self._srv.accept()
            except OSError:
                break
            with self._lock:
                agent_id = self._next_id
                self._next_id += 1
            threading.Thread(
                target=self._handle_agent,
                args=(conn, addr, agent_id),
                daemon=True,
            ).start()

    def _handle_agent(self, conn, addr, agent_id):
        with self._lock:
            self._agents[agent_id] = {"conn": conn, "addr": addr}
        self._emit(self.on_connect, agent_id, addr)
        try:
            while True:
                msg = recv_message(conn)
                if msg is None:
                    break
                status = msg.get("status", "")
                message = msg.get("message", "")
                self._emit(self.on_message, agent_id, addr, status, message, msg)
        except (ConnectionResetError, BrokenPipeError, OSError):
            pass
        finally:
            with self._lock:
                self._agents.pop(agent_id, None)
            try:
                conn.close()
            except OSError:
                pass
            self._emit(self.on_disconnect, agent_id, addr)

    # ---- consultas -----------------------------------------------------------
    def snapshot(self):
        """Copia segura del diccionario de agentes conectados."""
        with self._lock:
            return {aid: dict(entry) for aid, entry in self._agents.items()}

    def agent_ids(self):
        with self._lock:
            return list(self._agents.keys())

    def _get(self, agent_id):
        with self._lock:
            return self._agents.get(agent_id)

    # ---- acciones ------------------------------------------------------------
    def send_command(self, agent_id, action, payload=None):
        """Envía un comando a un agente. Devuelve True si se pudo enviar."""
        entry = self._get(agent_id)
        if not entry:
            self._log("error", f"Agente #{agent_id} no encontrado")
            return False
        try:
            entry["conn"].sendall(encode(create_message(action, payload)))
        except OSError as e:
            self._log("error", f"No se pudo enviar a #{agent_id}: {e}")
            return False
        self._emit(self.on_sent, agent_id, entry["addr"], action, payload)
        return True

    def broadcast(self, action, payload=None):
        """Envía un comando a todos los agentes. Devuelve cuántos lo recibieron."""
        ids = self.agent_ids()
        if not ids:
            self._log("warn", "No hay agentes conectados")
            return 0
        sent = sum(1 for aid in ids if self.send_command(aid, action, payload))
        self._log("info", f"Comando '{action}' enviado a {sent} agente(s)")
        return sent

    def kick(self, agent_id):
        """Desconecta a un agente cerrando su socket."""
        entry = self._get(agent_id)
        if not entry:
            self._log("error", f"Agente #{agent_id} no encontrado")
            return False
        try:
            entry["conn"].close()
        except OSError:
            pass
        return True
