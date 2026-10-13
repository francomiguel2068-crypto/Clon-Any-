"""Test de integración mínimo del ServerCore + agente real por sockets."""
import socket
import threading
import time
import unittest

from server.core import ServerCore
from shared.protocol import recv_message, encode, create_response


def _fake_agent(host, port, ready, got):
    """Un agente de juguete que se conecta, responde al primer comando y cierra."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for _ in range(50):
        try:
            s.connect((host, port))
            break
        except OSError:
            time.sleep(0.02)
    ready.set()
    msg = recv_message(s)
    if msg:
        got.append(msg)
        s.sendall(encode(create_response(msg["request_id"], "ok", "recibido")))
    time.sleep(0.1)
    s.close()


class TestServerCore(unittest.TestCase):

    def test_connect_send_and_receive(self):
        # Puerto 0 = el SO asigna uno libre (evita choques en CI).
        server = ServerCore("127.0.0.1", 0)
        server.start()
        real_port = server._srv.getsockname()[1]

        received = []
        connected = threading.Event()
        responded = threading.Event()
        server.on_connect = lambda aid, addr: connected.set()
        server.on_message = lambda aid, addr, st, msg, raw: responded.set()

        ready = threading.Event()
        got = []
        t = threading.Thread(target=_fake_agent, args=("127.0.0.1", real_port, ready, got), daemon=True)
        t.start()

        self.assertTrue(connected.wait(timeout=3), "el agente no se conectó")
        # El agente debe aparecer en el snapshot.
        self.assertEqual(len(server.snapshot()), 1)

        aid = server.agent_ids()[0]
        self.assertTrue(server.send_command(aid, "ping"))

        self.assertTrue(responded.wait(timeout=3), "no llegó la respuesta del agente")
        self.assertEqual(got[0]["action"], "ping")

        server.stop()
        t.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
