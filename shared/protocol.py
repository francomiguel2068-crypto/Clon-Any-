"""
Protocolo de comunicación SARE.
Define la serialización/deserialización de mensajes.
"""
import json
import struct
from datetime import datetime, timezone
from uuid import uuid4


def create_message(action: str, payload: dict = None) -> dict:
    """Crea un mensaje con formato estándar."""
    return {
        "type": "command",
        "action": action,
        "payload": payload or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": str(uuid4()),
    }


def create_response(request_id: str, status: str, message: str = "") -> dict:
    """Crea una respuesta estándar del agente."""
    return {
        "type": "response",
        "request_id": request_id,
        "status": status,
        "message": message,
    }


def encode(msg: dict) -> bytes:
    """Serializa un mensaje a bytes con prefijo de longitud (4 bytes)."""
    data = json.dumps(msg).encode("utf-8")
    return struct.pack("!I", len(data)) + data


def decode(data: bytes) -> dict:
    """Deserializa bytes a un diccionario."""
    return json.loads(data.decode("utf-8"))


def recv_message(sock) -> dict:
    """Lee un mensaje completo desde un socket TCP."""
    raw_len = _recv_exact(sock, 4)
    if not raw_len:
        return None
    msg_len = struct.unpack("!I", raw_len)[0]
    raw_msg = _recv_exact(sock, msg_len)
    if not raw_msg:
        return None
    return decode(raw_msg)


def _recv_exact(sock, n: int) -> bytes:
    """Lee exactamente n bytes del socket."""
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            return None
        data += chunk
    return data