import shutil

RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
ITALIC  = "\033[3m"
UNDER   = "\033[4m"

BLACK   = "\033[30m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
MAGENTA = "\033[35m"
CYAN    = "\033[36m"
WHITE   = "\033[37m"

BG_RED     = "\033[41m"
BG_GREEN   = "\033[42m"
BG_YELLOW  = "\033[43m"
BG_BLUE    = "\033[44m"
BG_MAGENTA = "\033[45m"
BG_CYAN    = "\033[46m"

BRIGHT_BLACK   = "\033[90m"
BRIGHT_RED     = "\033[91m"
BRIGHT_GREEN   = "\033[92m"
BRIGHT_YELLOW  = "\033[93m"
BRIGHT_BLUE    = "\033[94m"
BRIGHT_MAGENTA = "\033[95m"
BRIGHT_CYAN    = "\033[96m"
BRIGHT_WHITE   = "\033[97m"


def cols():
    return shutil.get_terminal_size((80, 24)).columns


def hr(char="─", color=BRIGHT_BLACK):
    return f"{color}{char * cols()}{RESET}"


def badge(text, bg=BG_CYAN, fg=BLACK):
    return f"{BOLD}{bg}{fg} {text} {RESET}"


def success(msg):
    return f"  {BRIGHT_GREEN}✔{RESET}  {msg}"


def error(msg):
    return f"  {BRIGHT_RED}✖{RESET}  {msg}"


def warn(msg):
    return f"  {BRIGHT_YELLOW}⚠{RESET}  {msg}"


def info(msg):
    return f"  {BRIGHT_CYAN}ℹ{RESET}  {msg}"


def arrow_right(msg):
    return f"  {BRIGHT_MAGENTA}➜{RESET}  {msg}"


def arrow_left(msg):
    return f"  {BRIGHT_BLUE}◀{RESET}  {msg}"


def dim(msg):
    return f"{DIM}{msg}{RESET}"


BANNER_SERVER = f"""
{BRIGHT_CYAN}{BOLD}  ╔═══════════════════════════════════════════════════╗
  ║                                                   ║
  ║   {BRIGHT_WHITE}███████╗ █████╗ ██████╗ ███████╗{BRIGHT_CYAN}               ║
  ║   {BRIGHT_WHITE}██╔════╝██╔══██╗██╔══██╗██╔════╝{BRIGHT_CYAN}               ║
  ║   {BRIGHT_GREEN}███████╗███████║██████╔╝█████╗  {BRIGHT_CYAN}               ║
  ║   {BRIGHT_GREEN}╚════██║██╔══██║██╔══██╗██╔══╝  {BRIGHT_CYAN}               ║
  ║   {BRIGHT_MAGENTA}███████║██║  ██║██║  ██║███████╗{BRIGHT_CYAN}               ║
  ║   {BRIGHT_MAGENTA}╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝{BRIGHT_CYAN}               ║
  ║                                                   ║
  ║   {DIM}{WHITE}Sistema de Administración Remota de Equipos{RESET}{BRIGHT_CYAN}{BOLD}    ║
  ║   {BRIGHT_YELLOW}▸ SERVIDOR / CONSOLA{BRIGHT_CYAN}                            ║
  ╚═══════════════════════════════════════════════════╝{RESET}
"""

BANNER_AGENT = f"""
{BRIGHT_BLUE}{BOLD}  ╔═══════════════════════════════════════════════════╗
  ║                                                   ║
  ║   {BRIGHT_WHITE}███████╗ █████╗ ██████╗ ███████╗{BRIGHT_BLUE}               ║
  ║   {BRIGHT_WHITE}██╔════╝██╔══██╗██╔══██╗██╔════╝{BRIGHT_BLUE}               ║
  ║   {BRIGHT_CYAN}███████╗███████║██████╔╝█████╗  {BRIGHT_BLUE}               ║
  ║   {BRIGHT_CYAN}╚════██║██╔══██║██╔══██╗██╔══╝  {BRIGHT_BLUE}               ║
  ║   {BRIGHT_MAGENTA}███████║██║  ██║██║  ██║███████╗{BRIGHT_BLUE}               ║
  ║   {BRIGHT_MAGENTA}╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝{BRIGHT_BLUE}               ║
  ║                                                   ║
  ║   {DIM}{WHITE}Sistema de Administración Remota de Equipos{RESET}{BRIGHT_BLUE}{BOLD}    ║
  ║   {BRIGHT_GREEN}▸ AGENTE / CLIENTE{BRIGHT_BLUE}                              ║
  ╚═══════════════════════════════════════════════════╝{RESET}
"""

AGENT_COMMANDS = [
    ("lock_screen",   "Bloquear pantalla"),
    ("unlock_screen", "Desbloquear pantalla"),
    ("ping",          "Test de conectividad"),
    ("screenshot",    "Captura de pantalla"),
    ("sysinfo",       "Info del sistema"),
    ("list_procs",    "Listar procesos"),
    ("kill_proc",     "Matar proceso (payload: pid)"),
    ("open_url",      "Abrir URL en navegador (payload: url)"),
    ("show_msg",      "Mostrar mensaje emergente (payload: text)"),
    ("shutdown",      "Apagar equipo"),
    ("restart",       "Reiniciar equipo"),
    ("logout",        "Cerrar sesión"),
]


def print_help_server():
    print()
    print(f"  {BOLD}{BRIGHT_WHITE}Comandos del servidor:{RESET}")
    print(f"  {hr('─', BRIGHT_BLACK)}")
    print(f"    {BRIGHT_CYAN}list{RESET}                  {DIM}│{RESET}  Ver agentes conectados")
    print(f"    {BRIGHT_CYAN}send{RESET} {DIM}<n> <cmd>{RESET}        {DIM}│{RESET}  Enviar comando al agente n")
    print(f"    {BRIGHT_CYAN}sendp{RESET} {DIM}<n> <cmd> <json>{RESET}{DIM}│{RESET}  Enviar comando con payload JSON")
    print(f"    {BRIGHT_CYAN}broadcast{RESET} {DIM}<cmd>{RESET}       {DIM}│{RESET}  Enviar comando a todos")
    print(f"    {BRIGHT_CYAN}kick{RESET} {DIM}<n>{RESET}              {DIM}│{RESET}  Desconectar agente n")
    print(f"    {BRIGHT_CYAN}clear{RESET}                 {DIM}│{RESET}  Limpiar pantalla")
    print(f"    {BRIGHT_CYAN}help{RESET}                  {DIM}│{RESET}  Mostrar esta ayuda")
    print(f"    {BRIGHT_CYAN}quit{RESET}                  {DIM}│{RESET}  Salir del servidor")
    print(f"  {hr('─', BRIGHT_BLACK)}")
    print(f"  {BOLD}{BRIGHT_WHITE}Comandos de agente:{RESET}")
    print(f"  {hr('─', BRIGHT_BLACK)}")
    for cmd, desc in AGENT_COMMANDS:
        print(f"    {BRIGHT_GREEN}{cmd:<18}{RESET}{DIM}│{RESET}  {desc}")
    print(f"  {hr('─', BRIGHT_BLACK)}")
    print(f"    {DIM}Ejemplo: send 0 lock_screen{RESET}")
    print(f"    {DIM}Ejemplo: sendp 0 show_msg {{\"text\":\"Hola clase\"}}{RESET}")
    print(f"    {DIM}Ejemplo: sendp 0 kill_proc {{\"pid\":1234}}{RESET}")
    print()


def print_agent_table(agents_dict):
    if not agents_dict:
        print(warn("Sin agentes conectados"))
        return
    print()
    print(f"    {BOLD}{BRIGHT_WHITE}{'ID':<6} {'Dirección':<25} {'Estado'}{RESET}")
    print(f"    {BRIGHT_BLACK}{'─'*6} {'─'*25} {'─'*12}{RESET}")
    for agent_id, entry in agents_dict.items():
        addr = entry["addr"]
        ip, port = addr
        print(f"    {BRIGHT_YELLOW}#{agent_id:<5}{RESET} {WHITE}{ip}:{port:<18}{RESET} {BRIGHT_GREEN}● online{RESET}")
    print(f"\n    {DIM}Total: {len(agents_dict)} agente(s){RESET}")
    print()
