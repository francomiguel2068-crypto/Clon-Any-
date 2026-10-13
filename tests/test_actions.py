"""Tests de agent/actions.py (comandos del agente)."""
import unittest

from agent import actions
from shared.commands import BY_ACTION, COMMANDS


class TestActions(unittest.TestCase):

    def setUp(self):
        # Partimos siempre con los comandos de energía desactivados.
        actions.set_power(False)

    def test_ping(self):
        status, msg = actions.dispatch("ping", {})
        self.assertEqual(status, "ok")
        self.assertEqual(msg, "pong")

    def test_unknown_command(self):
        status, msg = actions.dispatch("no_existe", {})
        self.assertEqual(status, "error")
        self.assertIn("desconocido", msg)

    def test_sysinfo_contains_os(self):
        status, msg = actions.dispatch("sysinfo", {})
        self.assertEqual(status, "ok")
        self.assertIn("OS=", msg)

    def test_show_msg_requires_text(self):
        status, msg = actions.dispatch("show_msg", {})
        self.assertEqual(status, "ok")  # dispatch no lanza; el handler avisa
        self.assertIn("falta", msg.lower())

    def test_power_disabled_by_default(self):
        status, msg = actions.dispatch("shutdown", {})
        self.assertEqual(status, "ok")
        self.assertIn("deshabilitado", msg.lower())

    def test_kill_proc_disabled_by_default(self):
        status, msg = actions.dispatch("kill_proc", {"pid": 99999})
        self.assertEqual(status, "ok")
        self.assertIn("deshabilitado", msg.lower())

    def test_kill_proc_invalid_pid(self):
        actions.set_power(True)
        try:
            status, msg = actions.dispatch("kill_proc", {"pid": "abc"})
        finally:
            actions.set_power(False)
        self.assertEqual(status, "ok")
        self.assertIn("inválido", msg.lower())

    def test_every_catalog_command_has_a_handler(self):
        for cmd in COMMANDS:
            self.assertIn(
                cmd["action"], actions.COMMAND_HANDLERS,
                f"Falta handler para {cmd['action']}",
            )

    def test_catalog_lookup(self):
        self.assertTrue(BY_ACTION["shutdown"]["power"])
        self.assertFalse(BY_ACTION["ping"]["power"])


if __name__ == "__main__":
    unittest.main()
