# SARE — Sistema de Administración Remota de Equipos

Herramienta **cliente-servidor para la gestión de un aula / laboratorio de cómputo**
en red local (LAN). Pensada para que el profesor administre los PCs del aula desde
su equipo: enviarles mensajes, bloquear la pantalla, abrir una página, ver
información del sistema y (opcionalmente) apagarlos o reiniciarlos al final de la
clase. Es la misma idea de programas como Veyon o NetSupport School, hecha con fines
educativos.

> Proyecto de la Media Técnica — **SENA 2026**. Todo el código es transparente: el
> agente que corre en cada PC muestra una ventana/consola con lo que recibe y hace;
> no se oculta ni se instala a escondidas.

---

## ✨ Qué incluye

- **Consola con interfaz gráfica** (el "front"): ventana donde el profesor ve los
  equipos conectados, envía comandos con botones y revisa un registro en vivo.
- **También consola de texto** clásica, para quien prefiera la terminal.
- **Agente** que corre en cada PC del aula, con **reconexión automática**: se puede
  encender en cualquier orden y se reconecta solo cuando aparece el servidor.
- **Instalable sin internet**: se generan dos ejecutables `.exe` (uno para el
  profesor, otro para los estudiantes) que **no necesitan instalar Python ni
  descargar nada** en los equipos de la escuela.
- **Cero dependencias en ejecución**: todo usa la librería estándar de Python
  (incluida Tkinter para la interfaz).

---

## ⚡ Lo más rápido para probar (Windows)

Hay lanzadores de **doble clic** (no hay que escribir comandos):

| Archivo | Para qué |
|---------|----------|
| `Probar-en-este-PC.bat` | Abre servidor + agente en el mismo PC y comprueba que todo funciona. |
| `Iniciar-Servidor.bat` | En el PC del profesor. Muestra la IP de ese PC y abre la consola. |
| `Iniciar-Agente.bat` | En el PC del estudiante. Pide la IP del profesor y se conecta. |

Guía corta en [COMO-PROBAR.txt](COMO-PROBAR.txt). Funcionan tanto con los `.exe`
como ejecutando el código fuente (si hay Python instalado).

> **Importante para dos PC:** el agente debe apuntar a la **IP del PC del
> profesor** (ej. `192.168.1.10`), no a `127.0.0.1` (que significa "este mismo
> PC"). Y si Windows pregunta por el Firewall en el servidor, hay que
> **"Permitir acceso"**.

## 🚀 Dos formas de usarlo

### A) Como ejecutables `.exe` (para los PCs de la escuela, sin internet)

Esta es la forma pensada para tu caso: los PCs del SENA son Windows y no tienen
internet.

#### Opción fácil: descargar los `.exe` ya compilados (no compilas nada)

El repositorio incluye una automatización (GitHub Actions) que compila los
ejecutables en un Windows real cada vez que se sube código. Para obtenerlos:

1. Entra al repositorio en GitHub, pestaña **Actions**.
2. Abre la última ejecución de **"Compilar ejecutables Windows"** (marca verde ✓).
3. Descarga el artifact **`SARE-Windows`** (un `.zip` con los dos `.exe` y el
   `sare_agente.ini`).

> Si en su lugar publicas una versión con un *tag* `v1.0`, los `.exe` quedan
> también en **Releases**, listos para descargar directamente.

Esto se hace una vez en un PC con internet; luego copias el `.zip` por USB y los
equipos del aula funcionan sin conexión. Si prefieres compilarlos tú mismo, sigue
la opción manual de abajo.

#### Opción manual: compilar tú mismo

**1. En TU PC (el que sí tiene internet), compila una sola vez.**
   Doble clic en:

   ```
   build\build_windows.bat
   ```

   El script instala PyInstaller (solo esa vez necesita internet) y genera en la
   carpeta `dist\`:

   - `SARE-Servidor.exe` → para el PC del profesor
   - `SARE-Agente.exe` → para los PCs de los estudiantes
   - `sare_agente.ini` → archivo de configuración de ejemplo del agente

**2. Copia los ejecutables a los PCs del aula** con una USB:

   | Equipo | Qué copiar |
   |--------|------------|
   | PC del profesor (servidor) | `SARE-Servidor.exe` |
   | Cada PC de estudiante (agente) | `SARE-Agente.exe` + `sare_agente.ini` |

**3. Configura la IP del profesor.** En cada PC de estudiante, abre
   `sare_agente.ini` con el Bloc de notas y pon la IP del PC del profesor:

   ```ini
   [servidor]
   host = 192.168.1.10      ; <-- IP del PC del profesor en la LAN
   port = 9001
   allow_power = false      ; true = permite apagar/reiniciar/cerrar sesión
   ```

   > Para saber la IP del profesor, en su PC ejecuta `ipconfig` y mira
   > "Dirección IPv4" de la red local.

**4. Usa el sistema.**
   - En el PC del profesor: doble clic en `SARE-Servidor.exe` (se abre la ventana).
   - En cada PC de estudiante: doble clic en `SARE-Agente.exe`.
   - Los equipos aparecen en la lista del servidor; selecciona uno (o marca
     "Aplicar a TODOS") y pulsa un comando.

### B) Desde el código fuente (para desarrollar o probar en una sola máquina)

Requiere Python 3.10+ (no requiere instalar nada más).

```bash
# Servidor con interfaz gráfica
python run_server.py

# Servidor en modo consola de texto
python run_server.py --cli

# Agente (en otra terminal). Opcional: IP y puerto del servidor
python run_agent.py 127.0.0.1 9001
```

---

## 🧩 Comandos disponibles

| Comando | Qué hace en Windows | Seguro |
|---------|---------------------|:------:|
| `ping` | Prueba de conexión (responde `pong`) | ✅ |
| `sysinfo` | Muestra SO, equipo, arquitectura, versión | ✅ |
| `lock_screen` | Bloquea la pantalla (pide contraseña para volver) | ✅ |
| `show_msg` | Muestra un mensaje emergente al estudiante | ✅ |
| `open_url` | Abre una página web en el navegador | ✅ |
| `list_procs` | Lista los procesos en ejecución | ✅ |
| `screenshot` | Demo (el streaming real queda como mejora futura) | ✅ |
| `kill_proc` | Cierra un proceso por su PID | ⚠️ energía |
| `logout` | Cierra la sesión de Windows | ⚠️ energía |
| `restart` | Reinicia el equipo | ⚠️ energía |
| `shutdown` | Apaga el equipo | ⚠️ energía |

**Comandos de energía (⚠️):** por seguridad vienen **desactivados por defecto**, así
nadie apaga máquinas por accidente mientras prueba. Para habilitarlos en un PC, pon
`allow_power = true` en su `sare_agente.ini` (o arranca el agente con la variable de
entorno `SARE_ALLOW_POWER=1`).

En sistemas que no son Windows (macOS/Linux) estos comandos responden "simulado",
para poder desarrollar sin riesgo.

---

## 🏗️ Arquitectura

```
┌──────────────────────────────┐        ┌──────────────────────────────┐
│   SERVIDOR / CONSOLA          │        │   AGENTE (cada PC del aula)   │
│   (PC del profesor)           │        │                               │
│                               │  TCP   │                               │
│   server/gui.py  (ventana)    │◀──────▶│   agent/main.py               │
│   server/main.py (texto)      │  9001  │   agent/actions.py            │
│   server/core.py (red)        │        │   agent/config.py             │
└──────────────┬────────────────┘        └───────────────┬──────────────┘
               │                                          │
               └──────────── shared/ (protocolo común) ───┘
                     protocol.py · commands.py · ui.py
```

- **Transporte:** TCP en el puerto `9001`, con mensajes JSON prefijados por su
  longitud (4 bytes). Ver `shared/protocol.py`.
- **Concurrencia:** cada agente se atiende en su propio hilo; la interfaz gráfica
  recibe los eventos de red por una cola para no bloquearse.

### Estructura del proyecto

```
Clon-Any/
├── server/
│   ├── core.py        # Núcleo de red (sin interfaz, reutilizable)
│   ├── gui.py         # Interfaz gráfica (Tkinter)
│   └── main.py        # Consola de texto
├── agent/
│   ├── main.py        # Cliente con reconexión automática
│   ├── actions.py     # Qué hace cada comando (real en Windows / simulado fuera)
│   └── config.py      # Lee IP/puerto de args o de sare_agente.ini
├── shared/
│   ├── protocol.py    # Formato de mensajes (encode/decode)
│   ├── commands.py    # Catálogo de comandos (una sola fuente de verdad)
│   └── ui.py          # Estilos de la consola de texto
├── build/
│   ├── build.py          # Compilador multiplataforma (PyInstaller)
│   └── build_windows.bat # Compilador de un clic para Windows
├── tests/                # Pruebas unitarias y de integración
├── run_server.py         # Punto de entrada del servidor
├── run_agent.py          # Punto de entrada del agente
├── requirements.txt      # (vacío: ejecución sin dependencias)
└── requirements-build.txt # Solo para compilar: pyinstaller
```

---

## ✅ Pruebas

```bash
python -m unittest discover -s tests
```

Cubren el protocolo, el catálogo de comandos, las acciones del agente (incluido que
los comandos de energía estén apagados por defecto) y una prueba de integración real
del servidor por sockets.

---

## 🔒 Nota de uso responsable

SARE está hecho para administrar equipos **propios o de un laboratorio con el
conocimiento de quienes lo usan** (como cualquier software de gestión de aula).
El agente es visible y no oculta su actividad. No debe usarse para controlar equipos
sin autorización.

## 📄 Licencia

Proyecto educativo — SENA 2026.
