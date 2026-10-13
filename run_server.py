"""Punto de entrada del SERVIDOR (lo que empaqueta PyInstaller -> SARE-Servidor.exe).

Por defecto abre la interfaz gráfica. Con --cli abre la consola de texto.
"""
import os
import sys

# Silenciar el aviso del Tk antiguo en macOS (inofensivo; no afecta a Windows).
os.environ.setdefault("TK_SILENCE_DEPRECATION", "1")


def main():
    if "--cli" in sys.argv[1:]:
        from server.main import main as cli_main
        cli_main()
    else:
        from server.gui import main as gui_main
        gui_main()


if __name__ == "__main__":
    main()
