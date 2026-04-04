# SARE — Sistema de Administración Remota de Equipos

Sistema cliente-servidor para administración remota de equipos en redes LAN educativas. Permite al administrador enviar comandos (bloqueo de pantalla, reinicio, mensajes) y recibir stream de pantalla en tiempo real.

## Arquitectura

- **Servidor (Consola):** Orquesta comandos vía TCP, recibe stream vía UDP
- **Agente (Cliente):** Ejecuta comandos localmente, transmite pantalla

```
┌───────────────────────────────┐
│      CONSOLA (Servidor)       │
│   ┌──────────┬──────────┐     │
│   │TCP Server│UDP Server│     │
│   │  :9001   │  :9002   │     │
│   └────┬─────┴────┬─────┘     │
│        │          │           │
│   ┌────┴──────────┴─────┐     │
│   │   Command Manager   │     │
│   └─────────────────────┘     │
└───────────────────────────────┘
         │TCP       │UDP
         ▼          ▼
┌───────────────────────────────┐
│       AGENTE (Cliente)        │
│   ┌──────────┬──────────┐     │
│   │TCP Client│UDP Client│     │
│   └────┬─────┴────┬─────┘     │
│        │          │           │
│   ┌────┴──────────┴─────┐     │
│   │  Command Executor   │     │
│   └─────────────────────┘     │
└───────────────────────────────┘
```

## Stack Tecnológico

- Python 3.10+
- Sockets TCP/UDP (librería estándar)
- Threading para concurrencia

## Estructura del Proyecto

```
sare-proyecto/
├── docs/                    # Toda la documentación
│   ├── requisitos.md
│   ├── arquitectura.md
│   └── diccionario-datos.md
├── server/                  # Código de la consola (servidor)
│   ├── __init__.py
│   └── main.py
├── agent/                   # Código del agente (cliente)
│   ├── __init__.py
│   └── main.py
├── shared/                  # Código compartido (protocolo, constantes)
│   ├── __init__.py
│   ├── protocol.py
│   └── ui.py
├── tests/                   # Pruebas unitarias
├── .gitignore
├── README.md
└── requirements.txt
```

## Cómo ejecutar

### Servidor
```bash
python -m server.main
```

### Agente
```bash
python -m agent.main [IP_SERVIDOR] [PUERTO]
```

### Prueba rápida (misma máquina)
1. Abrir terminal 1: `python -m server.main`
2. Abrir terminal 2: `python -m agent.main`
3. En terminal 1, escribir `list` para ver al agente, luego `send 0 lock_screen`

## Comandos del servidor

| Comando | Descripción |
|---------|-------------|
| `list` | Ver agentes conectados |
| `send <n> <cmd>` | Enviar comando al agente n |
| `broadcast <cmd>` | Enviar comando a todos los agentes |
| `help` | Mostrar ayuda |
| `quit` | Salir del servidor |

## Comandos del agente

| Comando | Descripción |
|---------|-------------|
| `lock_screen` | Simula bloqueo de pantalla |
| `unlock_screen` | Simula desbloqueo de pantalla |
| `ping` | Test de conectividad (responde "pong") |

## Equipo

| Nombre | Rol |
|--------|-----|
| ... | Líder / Arquitecto |
| ... | Documentación + Tests |
| ... | Servidor (TCP) |
| ... | Agente + Protocolo |

## Licencia

Proyecto educativo — SENA 2026
