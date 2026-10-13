"""Interfaz gráfica (GUI) del servidor SARE, hecha con Tkinter/ttk.

Tkinter viene incluido en la librería estándar de Python, así que el ejecutable
no necesita descargar nada: funciona en los equipos de la escuela sin internet.

Se usa el motor de temas ttk con el tema "clam", que respeta los colores que
definimos tanto en Windows como en macOS (el Tk nativo de macOS, en cambio,
ignora los colores de los botones y los pinta en modo oscuro del sistema).

Diseño: panel de administración claro y sobrio, sin iconos decorativos. Un solo
significado por color: azul = acción, verde = en línea, rojo = energía/peligro.
"""
import queue
import tkinter as tk
from datetime import datetime
from tkinter import font as tkfont
from tkinter import messagebox, simpledialog, ttk

from server.core import ServerCore, HOST, PORT
from shared.commands import GROUPS, by_group

# ---- Paleta (tema claro) ---------------------------------------------------
BG = "#eef1f4"          # fondo de la ventana
CARD = "#ffffff"        # tarjetas / paneles
HEADER = "#ffffff"      # barra superior
BAR = "#e3e7ec"         # barra de estado inferior
BORDER = "#dde2e8"      # líneas finas
BORDER_STRONG = "#c6cdd6"
FG = "#1d2430"          # texto principal
FG_DIM = "#5b6572"      # texto secundario
FG_FAINT = "#9aa3ae"    # texto tenue
ACCENT = "#2563eb"      # azul de acción
ACCENT_DK = "#1d4ed8"
ACCENT_SOFT = "#e8f0fe"
DANGER = "#c23b3b"      # rojo de energía / peligro
DANGER_DK = "#a32f2f"
DANGER_SOFT = "#fcebec"
DANGER_BORDER = "#e3b7b7"
HOVER = "#e9edf2"
OK = "#1f9d57"          # verde en línea
LOG_BG = "#fbfcfd"


class ServerGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.events = queue.Queue()
        self.server = ServerCore(HOST, PORT)
        self._wire_callbacks()

        root.title("SARE  ·  Consola de administración de aula")
        root.configure(bg=BG)
        root.geometry("1000x680")
        root.minsize(900, 600)

        self._init_fonts()
        self._init_style()
        self._build_header()
        self._build_body()
        self._build_statusbar()

        self._refresh_agents()
        self.root.after(80, self._drain_events)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.after(200, self.start_server)

    # ---- tipografía / estilos ----------------------------------------------
    def _init_fonts(self):
        avail = set(tkfont.families())
        fam = "Segoe UI" if "Segoe UI" in avail else ("Helvetica Neue" if "Helvetica Neue" in avail else "Helvetica")
        self.fam = fam
        self.f_title = (fam, 15, "bold")
        self.f_sub = (fam, 10)
        self.f_section = (fam, 9, "bold")
        self.f_group = (fam, 9, "bold")
        self.f_body = (fam, 10)
        self.f_small = (fam, 9)
        self.f_btn = (fam, 10)
        self.f_status = (fam, 10, "bold")
        mono = "Menlo" if "Menlo" in avail else ("Consolas" if "Consolas" in avail else "Courier")
        self.f_mono_sm = (mono, 9)

    def _wire_callbacks(self):
        self.server.on_connect = lambda aid, addr: self.events.put(("connect", aid, addr))
        self.server.on_disconnect = lambda aid, addr: self.events.put(("disconnect", aid, addr))
        self.server.on_message = lambda aid, addr, st, msg, raw: self.events.put(("message", aid, addr, st, msg))
        self.server.on_sent = lambda aid, addr, act, pl: self.events.put(("sent", aid, addr, act, pl))
        self.server.on_log = lambda level, text: self.events.put(("log", level, text))

    def _init_style(self):
        st = ttk.Style()
        try:
            st.theme_use("clam")
        except tk.TclError:
            pass

        def button(name, bg, fg, hover, border):
            st.configure(name, background=bg, foreground=fg, bordercolor=border,
                         lightcolor=bg, darkcolor=bg, focuscolor=border, relief="flat",
                         font=self.f_btn, padding=(12, 8), anchor="w")
            st.map(name,
                   background=[("active", hover), ("pressed", hover)],
                   bordercolor=[("active", border)],
                   foreground=[("disabled", FG_FAINT)])

        button("Cmd.TButton", CARD, FG, HOVER, BORDER_STRONG)
        button("Danger.TButton", CARD, DANGER_DK, DANGER_SOFT, DANGER_BORDER)
        button("Ghost.TButton", CARD, FG_DIM, HOVER, BORDER)
        # Botones del encabezado (centrados)
        st.configure("Primary.TButton", background=ACCENT, foreground="#ffffff",
                     bordercolor=ACCENT, lightcolor=ACCENT, darkcolor=ACCENT,
                     focuscolor=ACCENT, relief="flat", font=self.f_btn, padding=(14, 7))
        st.map("Primary.TButton", background=[("active", ACCENT_DK), ("pressed", ACCENT_DK)])
        st.configure("Toggle.TButton", background=CARD, foreground=DANGER_DK,
                     bordercolor=BORDER_STRONG, lightcolor=CARD, darkcolor=CARD,
                     focuscolor=BORDER_STRONG, relief="flat", font=self.f_btn, padding=(14, 7))
        st.map("Toggle.TButton", background=[("active", DANGER_SOFT), ("pressed", DANGER_SOFT)])

        st.configure("Card.TCheckbutton", background=CARD, foreground=FG, font=self.f_body)
        st.map("Card.TCheckbutton", background=[("active", CARD)],
               indicatorcolor=[("selected", ACCENT), ("!selected", CARD)])

        st.configure("SARE.Treeview", background=CARD, fieldbackground=CARD, foreground=FG,
                     rowheight=30, borderwidth=0, font=self.f_body)
        st.configure("SARE.Treeview.Heading", background="#f1f4f7", foreground=FG_DIM,
                     relief="flat", font=self.f_section, padding=(10, 8))
        st.map("SARE.Treeview", background=[("selected", ACCENT_SOFT)], foreground=[("selected", FG)])
        st.configure("TScrollbar", background=BAR, troughcolor=CARD, bordercolor=CARD,
                     arrowcolor=FG_DIM)

    # ---- helpers de construcción -------------------------------------------
    def _card(self, parent, title):
        """Tarjeta blanca con borde fino y título de sección."""
        outer = tk.Frame(parent, bg=CARD, highlightbackground=BORDER,
                         highlightcolor=BORDER, highlightthickness=1)
        tk.Label(outer, text=title.upper(), font=self.f_section, fg=FG_DIM, bg=CARD,
                 anchor="w").pack(fill="x", padx=14, pady=(12, 8))
        tk.Frame(outer, bg=BORDER, height=1).pack(fill="x")
        inner = tk.Frame(outer, bg=CARD)
        inner.pack(fill="both", expand=True, padx=14, pady=12)
        return outer, inner

    def _build_header(self):
        bar = tk.Frame(self.root, bg=HEADER)
        bar.pack(fill="x", side="top")
        tk.Frame(bar, bg=BORDER, height=1).pack(fill="x", side="bottom")

        left = tk.Frame(bar, bg=HEADER)
        left.pack(side="left", padx=16, pady=12)
        tk.Label(left, text="SARE", font=self.f_title, fg=ACCENT, bg=HEADER).pack(side="left")
        tk.Label(left, text="   Administración remota de equipos", font=self.f_sub,
                 fg=FG_DIM, bg=HEADER).pack(side="left")

        right = tk.Frame(bar, bg=HEADER)
        right.pack(side="right", padx=16, pady=10)
        self.btn_toggle = ttk.Button(right, text="Iniciar servidor", style="Primary.TButton",
                                     command=self.toggle_server, takefocus=False)
        self.btn_toggle.pack(side="right", padx=(12, 0))
        self.status_text = tk.Label(right, text="Detenido", font=self.f_status, fg=FG_DIM, bg=HEADER)
        self.status_text.pack(side="right", padx=(0, 2))
        self.status_dot = tk.Label(right, text="●", font=(self.fam, 11), fg=DANGER, bg=HEADER)
        self.status_dot.pack(side="right", padx=(0, 6))

    def _build_body(self):
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=16, pady=(14, 8))

        # Panel derecho (ancho fijo) con los comandos
        right_wrap = tk.Frame(body, bg=BG, width=300)
        right_wrap.pack(side="right", fill="y", padx=(14, 0))
        right_wrap.pack_propagate(False)
        card_c, inner_c = self._card(right_wrap, "Comandos")
        card_c.pack(fill="both", expand=True)
        self._build_commands(inner_c)

        # Panel izquierdo: equipos + registro
        left = tk.Frame(body, bg=BG)
        left.pack(side="left", fill="both", expand=True)

        card_a, inner_a = self._card(left, "Equipos conectados")
        card_a.pack(fill="both", expand=True)
        self._build_agents(inner_a)

        card_log, inner_log = self._card(left, "Registro de actividad")
        card_log.pack(fill="both", expand=True, pady=(12, 0))
        self._build_log(inner_log)

    def _build_agents(self, parent):
        cols = ("id", "ip", "estado")
        self.tree = ttk.Treeview(parent, columns=cols, show="headings", height=6,
                                 style="SARE.Treeview")
        self.tree.heading("id", text="ID")
        self.tree.heading("ip", text="Dirección")
        self.tree.heading("estado", text="Estado")
        self.tree.column("id", width=48, anchor="center")
        self.tree.column("ip", width=220, anchor="w")
        self.tree.column("estado", width=110, anchor="w")
        self.tree.pack(fill="both", expand=True)
        self.tree.tag_configure("online", foreground=OK)

        actions = tk.Frame(parent, bg=CARD)
        actions.pack(fill="x", pady=(10, 0))
        self.all_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(actions, text="Aplicar a todos los equipos (broadcast)",
                        variable=self.all_var, style="Card.TCheckbutton",
                        takefocus=False).pack(side="left")
        ttk.Button(actions, text="Desconectar", style="Ghost.TButton",
                   command=self._kick_selected, takefocus=False).pack(side="right")

    def _build_log(self, parent):
        box = tk.Frame(parent, bg=LOG_BG, highlightbackground=BORDER, highlightthickness=1)
        box.pack(fill="both", expand=True)
        self.log = tk.Text(box, height=8, bg=LOG_BG, fg=FG, insertbackground=FG,
                           font=self.f_mono_sm, relief="flat", wrap="word", state="disabled",
                           padx=10, pady=8, highlightthickness=0, bd=0)
        scroll = ttk.Scrollbar(box, command=self.log.yview)
        self.log.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.log.pack(side="left", fill="both", expand=True)
        for tag, color in (("ok", OK), ("warn", "#b7791f"), ("error", DANGER),
                           ("info", ACCENT_DK), ("dim", FG_FAINT), ("in", OK), ("out", ACCENT_DK)):
            self.log.tag_configure(tag, foreground=color)

    def _build_commands(self, parent):
        parent.columnconfigure(0, weight=1)
        r = 0
        for gi, group in enumerate(GROUPS):
            cmds = by_group(group)
            if not cmds:
                continue
            tk.Label(parent, text=group, font=self.f_group, fg=FG_DIM, bg=CARD,
                     anchor="w").grid(row=r, column=0, sticky="ew", pady=(0 if gi == 0 else 12, 5))
            r += 1
            for cmd in cmds:
                style = "Danger.TButton" if cmd["power"] else "Cmd.TButton"
                ttk.Button(parent, text=cmd["label"], style=style, takefocus=False,
                           command=lambda c=cmd: self._send(c)).grid(
                    row=r, column=0, sticky="ew", pady=3)
                r += 1
        tk.Label(parent,
                 text="Los comandos en rojo son de energía; sólo actúan\n"
                      "en los equipos que los tengan habilitados.",
                 font=self.f_small, fg=FG_FAINT, bg=CARD, justify="left", anchor="w").grid(
            row=r, column=0, sticky="ew", pady=(14, 0))

    def _build_statusbar(self):
        self.bar = tk.Label(self.root, text=f"Escuchando en {HOST}:{PORT}", font=self.f_mono_sm,
                            fg=FG_DIM, bg=BAR, anchor="w", padx=14, pady=5)
        self.bar.pack(fill="x", side="bottom")

    # ---- acciones -----------------------------------------------------------
    def toggle_server(self):
        if self.server._running:
            self.stop_server()
        else:
            self.start_server()

    def start_server(self):
        if self.server._running:
            return
        try:
            self.server.start()
        except OSError as e:
            messagebox.showerror("SARE", f"No se pudo abrir el puerto {PORT}.\n\n{e}")
            return
        self.status_dot.configure(fg=OK)
        self.status_text.configure(text="En línea", fg=FG)
        self.btn_toggle.configure(text="Detener servidor", style="Toggle.TButton")

    def stop_server(self):
        self.server.stop()
        self.status_dot.configure(fg=DANGER)
        self.status_text.configure(text="Detenido", fg=FG_DIM)
        self.btn_toggle.configure(text="Iniciar servidor", style="Primary.TButton")
        self._refresh_agents()

    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            return None
        try:
            return int(self.tree.item(sel[0], "values")[0])
        except (ValueError, IndexError):
            return None

    def _send(self, cmd):
        payload = None
        if cmd["prompt"]:
            value = simpledialog.askstring("SARE · " + cmd["label"], cmd["prompt"], parent=self.root)
            if value is None or not value.strip():
                return
            payload = {cmd["prompt_key"]: value.strip()}

        to_all = self.all_var.get()

        if cmd["power"]:
            alcance = "TODOS los equipos" if to_all else "el equipo seleccionado"
            if not messagebox.askyesno(
                "Confirmar comando de energía",
                f"Vas a enviar «{cmd['label']}» a {alcance}.\n\n"
                "Sólo se ejecutará de verdad en los equipos que tengan los\n"
                "comandos de energía habilitados. ¿Continuar?",
            ):
                return

        if to_all:
            self.server.broadcast(cmd["action"], payload)
            return

        aid = self._selected_id()
        if aid is None:
            messagebox.showinfo("SARE", "Selecciona un equipo de la lista, o marca «Aplicar a todos».")
            return
        self.server.send_command(aid, cmd["action"], payload)

    def _kick_selected(self):
        aid = self._selected_id()
        if aid is None:
            messagebox.showinfo("SARE", "Selecciona un equipo para desconectar.")
            return
        self.server.kick(aid)

    # ---- eventos de red en el hilo de la interfaz ---------------------------
    def _drain_events(self):
        try:
            while True:
                self._handle_event(self.events.get_nowait())
        except queue.Empty:
            pass
        self.root.after(80, self._drain_events)

    def _handle_event(self, ev):
        kind = ev[0]
        if kind == "connect":
            _, aid, addr = ev
            self._log(f"Equipo #{aid} conectado  ({addr[0]}:{addr[1]})", "ok")
            self._refresh_agents()
        elif kind == "disconnect":
            _, aid, addr = ev
            self._log(f"Equipo #{aid} desconectado  ({addr[0]}:{addr[1]})", "warn")
            self._refresh_agents()
        elif kind == "message":
            _, aid, addr, st, msg = ev
            tag = "in" if st == "ok" else "error" if st == "error" else "dim"
            self._log(f"#{aid}  <-  {msg}", tag)
        elif kind == "sent":
            _, aid, addr, act, pl = ev
            extra = f"   {pl}" if pl else ""
            self._log(f"#{aid}  ->  {act}{extra}", "out")
        elif kind == "log":
            _, level, text = ev
            self._log(text, level if level in ("ok", "warn", "error", "info") else "info")

    def _refresh_agents(self):
        snap = self.server.snapshot()
        self.tree.delete(*self.tree.get_children())
        for aid, entry in sorted(snap.items()):
            ip, port = entry["addr"]
            self.tree.insert("", "end", values=(aid, f"{ip}:{port}", "En línea"), tags=("online",))
        self.bar.configure(
            text=f"Escuchando en {HOST}:{PORT}      {len(snap)} equipo(s) conectado(s)")

    def _log(self, text, tag="info"):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log.configure(state="normal")
        self.log.insert("end", f"{ts}  ", "dim")
        self.log.insert("end", f"{text}\n", tag)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _on_close(self):
        self.server.stop()
        self.root.destroy()


def main():
    root = tk.Tk()
    ServerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
