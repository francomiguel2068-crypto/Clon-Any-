"""Catálogo compartido de comandos de agente.

Una sola fuente de verdad para la consola, la interfaz gráfica y el agente.
Cada comando declara:
  - action:      identificador que viaja por la red
  - label:       texto para mostrar en la interfaz
  - group:       sección a la que pertenece en la interfaz
  - prompt:      si no es None, la interfaz pide ese texto y lo mete en el payload
  - prompt_key:  nombre del campo del payload donde va lo que escriba el usuario
  - power:       True si es un comando de energía/peligroso (apagar, kill, etc.)
"""

# Orden en que se muestran las secciones en la interfaz.
GROUPS = ["Conexión", "Pantalla y aula", "Procesos", "Energía"]

COMMANDS = [
    {"action": "ping",          "label": "Probar conexión",        "group": "Conexión",
     "prompt": None, "prompt_key": None, "power": False},
    {"action": "sysinfo",       "label": "Información del sistema", "group": "Conexión",
     "prompt": None, "prompt_key": None, "power": False},

    {"action": "lock_screen",   "label": "Bloquear pantalla",      "group": "Pantalla y aula",
     "prompt": None, "prompt_key": None, "power": False},
    {"action": "unlock_screen", "label": "Desbloquear",            "group": "Pantalla y aula",
     "prompt": None, "prompt_key": None, "power": False},
    {"action": "show_msg",      "label": "Enviar mensaje",         "group": "Pantalla y aula",
     "prompt": "Texto del mensaje a mostrar:", "prompt_key": "text", "power": False},
    {"action": "open_url",      "label": "Abrir página web",       "group": "Pantalla y aula",
     "prompt": "Dirección web (https://...):", "prompt_key": "url", "power": False},
    {"action": "screenshot",    "label": "Captura de pantalla",    "group": "Pantalla y aula",
     "prompt": None, "prompt_key": None, "power": False},

    {"action": "list_procs",    "label": "Listar procesos",        "group": "Procesos",
     "prompt": None, "prompt_key": None, "power": False},
    {"action": "kill_proc",     "label": "Finalizar proceso",      "group": "Procesos",
     "prompt": "PID del proceso a finalizar:", "prompt_key": "pid", "power": True},

    {"action": "logout",        "label": "Cerrar sesión",          "group": "Energía",
     "prompt": None, "prompt_key": None, "power": True},
    {"action": "restart",       "label": "Reiniciar equipo",       "group": "Energía",
     "prompt": None, "prompt_key": None, "power": True},
    {"action": "shutdown",      "label": "Apagar equipo",          "group": "Energía",
     "prompt": None, "prompt_key": None, "power": True},
]

# Acceso rápido por nombre de acción.
BY_ACTION = {c["action"]: c for c in COMMANDS}


def by_group(group: str):
    """Comandos de una sección, en orden."""
    return [c for c in COMMANDS if c["group"] == group]


def is_power(action: str) -> bool:
    cmd = BY_ACTION.get(action)
    return bool(cmd and cmd["power"])
