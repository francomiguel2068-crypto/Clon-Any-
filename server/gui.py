"""Interfaz gráfica (GUI) del servidor SARE, hecha con Tkinter.

Tkinter viene incluido en la librería estándar de Python, así que el ejecutable
no necesita descargar nada: funciona en los equipos de la escuela sin internet.

Diseño: panel de administración sobrio y profesional, sin iconos decorativos.
Color con un solo significado por tono:
  - azul   = acción / foco / estado en línea del servidor
  - rojo   = comandos de energía (apagar, reiniciar, finalizar proceso)
  - verde  = equipo conectado / respuesta correcta
Toda la red corre en hilos aparte; los eventos llegan a la interfaz por una cola.
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
BORDER = "#dde2e8"      # líneas finas
BORDER_STRONG = "#c6cdd6"
FG = "#1d2430"          # texto principal
FG_DIM = "#5b6572"      # texto secundario
FG_FAINT = "#9aa3ae"    # texto tenue / horas del registro
ACCENT = "#2563eb"      # azul de acción
ACCENT_DK = "#1d4ed8"
ACCENT_SOFT = "#e8f0fe"
DANGER = "#c23b3b"      # rojo de energía / peligro
DANGER_DK = "#a32f2f"
DANGER_SOFT = "#fcebec"
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
        root.minsize(880, 600)

        self._init_fonts()
        self._init_ttk_style()
        self._build_header()
        self._build_body()
        self._build_statusbar()

        self._refresh_agents()
        self.root.after(80, self._drain_events)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.after(200, self.start_server)

    # ---- tipografía ---------------------------------------------------------
    def _init_fonts(self):
        fam = "Segoe UI"
        available = set(tkfont.families())
        if fam not in available:
            fam = "Helvetica"
        self.f_title = (fam, 15, "bold")
        self.f_sub = (fam, 10)
        self.f_section = (fam, 9, "bold")
        self.f_body = (fam, 10)
        self.f_small = (fam, 9)
        self.f_btn = (fam, 10)
        mono = "Consolas" if "Consolas" in available else "Courier"
        self.f_mono = (mono, 10)
        self.f_mono_sm = (mono, 9)

    def _wire_callbacks(self):
        self.server.on_connect = lambda aid, addr: self.events.put(("connect", aid, addr))
        self.server.on_disconnect = lambda aid, addr: self.events.put(("disconnect", aid, addr))
        self.server.on_message = lambda aid, addr, st, msg, raw: self.events.put(("message", aid, addr, st, msg))
        self.server.on_sent = lambda aid, addr, act, pl: self.events.put(("sent", aid, addr, act, pl))
        self.server.on_log = lambda level, text: self.events.put(("log", level, text))

    def _init_ttk_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "SARE.Treeview", background=CARD, fieldbackground=CARD, foreground=FG,
            rowheight=30, borderwidth=0, font=self.f_body,
        )
        style.configure(
            "SARE.Treeview.Heading", background="#f1f4f7", foreground=FG_DIM,
            relief="flat", font=self.f_section, padding=(10, 8),
        )
        style.map(
            "SARE.Treeview",
            background=[("selected", ACCENT_SOFT)],
            foreground=[("selected", FG)],
        )

    # ---- construcción -------------------------------------------------------
    def _button(self, parent, text, command, kind="default"):
        """Botón plano con estilo coherente. kind: default | primary | danger | ghost."""
        if kind == "primary":
            bg, fg, abg = ACCENT, "#ffffff", ACCENT_DK
        elif kind == "danger":
            bg, fg, abg = CARD, DANGER_DK, DANGER_SOFT
        elif kind == "ghost":
            bg, fg, abg = CARD, FG_DIM, "#eef1f4"
        else:
            bg, fg, abg = CARD, FG, "#eef1f4"
        b = tk.Button(
            parent, text=text, command=command, bg=bg, fg=fg,
            activebackground=abg, activeforeground=fg, font=self.f_btn,
            relief="flat", bd=0, highlightthickness=1,
            highlightbackground=DANGER if kind == "danger" else BORDER_STRONG,
            highlightcolor=BORDER_STRONG, cursor="hand2",
            padx=10, pady=7, anchor="w", justify="left",
        )
        return b

    def _build_header(self):
        bar = tk.Frame(self.root, bg=HEADER, highlightbackground=BORDER,
                       highlightthickness=0)
        bar.pack(fill="x", side="top")
        tk.Frame(bar, bg=BORDER, height=1).pack(fill="x", side="bottom")

        left = tk.Frame(bar, bg=HEADER)
        left.pack(side="left", padx=16, pady=12)
        tk.Label(left, text="SARE", font=self.f_title, fg=ACCENT, bg=HEADER).pack(side="left")
        tk.Label(left, text="   Administración remota de equipos", font=self.f_sub,
                 fg=FG_DIM, bg=HEADER).pack(side="left")

        right = tk.Frame(bar, bg=HEADER)
        right.pack(side="right", padx=16, pady=10)
        self.btn_toggle = self._button(right, "Iniciar servidor", self.toggle_server, kind="primary")
        self.btn_toggle.pack(side="right", padx=(12, 0))
        self.status_text = tk.Label(right, text="Detenido", font=(self.f_body[0], 10, "bold"),
                                    fg=FG_DIM, bg=HEADER)
        self.status_text.pack(side="right", padx=(0, 2))
        self.status_dot = tk.Label(right, text="●", font=(self.f_body[0], 11),
                                   fg=DANGER, bg=HEADER)
        self.status_dot.pack(side="right", padx=(0, 6))

    def _card(self, parent, title):
        """Una tarjeta blanca con título de sección. Devuelve el frame interno."""
        outer = tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        tk.Label(outer, text=title.upper(), font=self.f_section, fg=FG_DIM, bg=CARD,
                 anchor="w").pack(fill="x", padx=14, pady=(12, 8))
        tk.Frame(outer, bg=BORDER, height=1).pack(fill="x", padx=0)
        inner = tk.Frame(outer, bg=CARD)
        inner.pack(fill="both", expand=True, padx=14, pady=12)
        return outer, inner

    def _build_body(self):
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=16, pady=(14, 8))

        # --- Izquierda: equipos + registro ---
        left = tk.Frame(body, bg=BG)
        left.pack(side="left", fill="both", expand=True)

        card_a, inner_a = self._card(left, "Equipos conectados")
        card_a.pack(fill="both", expand=True)

        cols = ("id", "ip", "estado")
        self.tree = ttk.Treeview(inner_a, columns=cols, show="headings", height=6,
                                 style="SARE.Treeview")
        self.tree.heading("id", text="ID")
        self.tree.heading("ip", text="Dirección")
        self.tree.heading("estado", text="Estado")
        self.tree.column("id", width=48, anchor="center")
        self.tree.column("ip", width=220, anchor="w")
        self.tree.column("estado", width=110, anchor="w")
        self.tree.pack(fill="both", expand=True)

        actions = tk.Frame(inner_a, bg=CARD)
        actions.pack(fill="x", pady=(10, 0))
        self.all_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            actions, text="Aplicar a todos los equipos (broadcast)", variable=self.all_var,
            fg=FG, bg=CARD, selectcolor=CARD, activebackground=CARD, activeforeground=FG,
            font=self.f_body, highlightthickness=0, bd=0, anchor="w",
        ).pack(side="left")
        self._button(actions, "Desconectar", self._kick_selected, kind="ghost").pack(side="right")

        card_log, inner_log = self._card(left, "Registro de actividad")
        card_log.pack(fill="both", expand=True, pady=(12, 0))
        logbox = tk.Frame(inner_log, bg=LOG_BG, highlightbackground=BORDER, highlightthickness=1)
        logbox.pack(fill="both", expand=True)
        self.log = tk.Text(logbox, height=8, bg=LOG_BG, fg=FG, insertbackground=FG,
                           font=self.f_mono_sm, relief="flat", wrap="word", state="disabled",
                           padx=10, pady=8, highlightthickness=0, bd=0)
        scroll = ttk.Scrollbar(logbox, command=self.log.yview)
        self.log.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.log.pack(side="left", fill="both", expand=True)
        self.log.tag_configure("ok", foreground=OK)
        self.log.tag_configure("warn", foreground="#b7791f")
        self.log.tag_configure("error", foreground=DANGER)
        self.log.tag_configure("info", foreground=ACCENT_DK)
        self.log.tag_configure("dim", foreground=FG_FAINT)
        self.log.tag_configure("in", foreground=OK)
        self.log.tag_configure("out", foreground=ACCENT_DK)

        # --- Derecha: comandos por secciones ---
        right = tk.Frame(body, bg=BG, width=300)
        right.pack(side="right", fill="y", padx=(14, 0))
        right.pack_propagate(False)

        card_c, inner_c = self._card(right, "Comandos")
        card_c.pack(fill="both", expand=True)

        for gi, group in enumerate(GROUPS):
            cmds = by_group(group)
            if not cmds:
                continue
            tk.Label(inner_c, text=group, font=(self.f_body[0], 9, "bold"),
                     fg=FG_DIM, bg=CARD, anchor="w").grid(
                row=gi * 10, column=0, columnspan=2, sticky="ew", pady=(0 if gi == 0 else 10, 4))
            for ci, cmd in enumerate(cmds):
                kind = "danger" if cmd["power"] else "default"
                b = self._button(inner_c, cmd["label"], lambda c=cmd: self._send(c), kind=kind)
                b.grid(row=gi * 10 + 1 + ci // 2, column=ci % 2, sticky="ew", padx=2, pady=3)
        inner_c.columnconfigure(0, weight=1)
        inner_c.columnconfigure(1, weight=1)

        hint = tk.Label(
            inner_c,
            text="Los comandos en rojo son de energía; sólo actúan en\n"
                 "los equipos que los tengan habilitados.",
            font=self.f_small, fg=FG_FAINT, bg=CARD, justify="left", anchor="w",
        )
        hint.grid(row=999, column=0, columnspan=2, sticky="ew", pady=(14, 0))

    def _build_statusbar(self):
        self.bar = tk.Label(
            self.root, text=f"Escuchando en {HOST}:{PORT}", font=self.f_mono_sm,
            fg=FG_DIM, bg="#e3e7ec", anchor="w", padx=14, pady=5,
        )
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
        self.btn_toggle.configure(text="Detener servidor", bg=CARD, fg=DANGER_DK,
                                  activebackground=DANGER_SOFT, highlightbackground=BORDER_STRONG)

    def stop_server(self):
        self.server.stop()
        self.status_dot.configure(fg=DANGER)
        self.status_text.configure(text="Detenido", fg=FG_DIM)
        self.btn_toggle.configure(text="Iniciar servidor", bg=ACCENT, fg="#ffffff",
                                  activebackground=ACCENT_DK, highlightbackground=BORDER_STRONG)
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
            self.tree.insert("", "end", values=(aid, f"{ip}:{port}", "En línea"))
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
