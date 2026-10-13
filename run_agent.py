"""Punto de entrada del AGENTE (lo que empaqueta PyInstaller -> SARE-Agente.exe).

Uso:  SARE-Agente.exe [IP_SERVIDOR] [PUERTO]
"""
from agent.main import main

if __name__ == "__main__":
    main()
