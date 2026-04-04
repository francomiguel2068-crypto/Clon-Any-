import json
import struct
from datetime import datetime, timezone
from uuid import uuid4


def create_message(action: str, payload: dict = None) -> dict:
    return {
        "type": "command",
        "action": action,
        "payload": payload or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": str(uuid4()),
    }


def create_response(request_id: str, status: str, message: str = "") -> dict:
    return {
        "type": "response",
        "request_id": request_id,
        "status": status,
        "message": message,
    }


def encode(msg: dict) -> bytes:
    data = json.dumps(msg).encode("utf-8")
    return struct.pack("!I", len(data)) + data


def decode(data: bytes) -> dict:
    return json.loads(data.decode("utf-8"))


def recv_message(sock) -> dict:
    try:
        raw_len = _recv_exact(sock, 4)
        if not raw_len:
            return None
        msg_len = struct.unpack("!I", raw_len)[0]
        raw_msg = _recv_exact(sock, msg_len)
        if not raw_msg:
            return None
        return decode(raw_msg)
    except OSError:
        return None


def _recv_exact(sock, n: int) -> bytes:
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            return None
        data += chunk
    return data
