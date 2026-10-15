# =====================================================================
#  PD-FileSync_V1.0 - Sistema de respaldos automático - S1 a Cortadoras
# =====================================================================
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json
import os
import sys
import threading
from pathlib import Path
from datetime import datetime

from replicador import Replicador


# =====================================================================
#  Constantes globales
# =====================================================================
APP_NOMBRE   = "FileSync_V1.0"
APP_TITULO   = "FileSync_V1.0 - Sistema de respaldos automático - Servidor 1 a Cortadoras"
VERSION      = "1.0"
COPYRIGHT    = "Copyright © 2026 Pro Dept. All rights reserved."
CREDITOS     = "Designed & Developed by PD-IT-MH"

# --- Paleta Windows 11 ---
COL_FONDO          = "#F3F3F3"
COL_PANEL          = "#FFFFFF"
COL_ACENTO         = "#0067C0"
COL_ACENTO_HOVER   = "#1976D2"
COL_TEXTO          = "#1F1F1F"
COL_TEXTO_SEC      = "#605E5C"
COL_BORDE          = "#E5E5E5"

COL_CONSOLE_BG     = "#1E1E1E"
COL_CONSOLE_FG     = "#D4D4D4"
COL_CONSOLE_OK     = "#4EC9B0"
COL_CONSOLE_WARN   = "#DCDCAA"
COL_CONSOLE_ERR    = "#F48771"
COL_CONSOLE_INFO   = "#569CD6"

FONT_BASE    = ("Segoe UI", 10)
FONT_BOLD    = ("Segoe UI", 10, "bold")
FONT_TITULO  = ("Segoe UI Semibold", 14)
FONT_SUBTIT  = ("Segoe UI", 9)
FONT_CONSOLA = ("Consolas", 9)


# =====================================================================
def ruta_base() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


CONFIG_PATH = ruta_base() / "config.json"


# =====================================================================
#  Ícono de PC dibujado
# =====================================================================
def crear_icono_pc() -> tk.PhotoImage:
    ico = tk.PhotoImage(width=32, height=32)
    azul     = "#0067C0"
    gris     = "#605E5C"
    pantalla = "#DCEBF8"
    brillo   = "#FFFFFF"

    for x in range(3, 29):
        for y in range(5, 22):
            ico.put(azul, (x, y))
    for x in range(5, 27):
        for y in range(7, 20):
            ico.put(pantalla, (x, y))
    for x in range(7, 15):
        for y in range(9, 12):
            ico.put(brillo, (x, y))
    for x in range(2, 30):
        for y in range(22, 25):
            ico.put(gris, (x, y))
    for x in range(13, 19):
        for y in range(25, 28):
            ico.put(gris, (x, y))
    for x in range(8, 24):
        for y in range(28, 31):
            ico.put(gris, (x, y))
    return ico


# =====================================================================
#  Estilos ttk globales
# =====================================================================
def aplicar_estilos(root):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    style.configure("TFrame", background=COL_FONDO)
    style.configure("Card.TFrame", background=COL_PANEL, relief="flat")

    style.configure("TLabel", background=COL_FONDO, foreground=COL_TEXTO, font=FONT_BASE)
    style.configure("Card.TLabel", background=COL_PANEL, foreground=COL_TEXTO, font=FONT_BASE)
    style.configure("Titulo.TLabel", background=COL_FONDO, foreground=COL_TEXTO,
                    font=FONT_TITULO)
    style.configure("Subtitulo.TLabel", background=COL_FONDO, foreground=COL_TEXTO_SEC,
                    font=FONT_SUBTIT)
    style.configure("Secundario.TLabel", background=COL_PANEL,
                    foreground=COL_TEXTO_SEC, font=FONT_SUBTIT)

    style.configure("Acento.TButton",
                    background=COL_ACENTO, foreground="white",
                    font=FONT_BOLD, borderwidth=0, focuscolor=COL_ACENTO,
                    padding=(14, 8))
    style.map("Acento.TButton",
              background=[("active", COL_ACENTO_HOVER), ("disabled", "#B0B0B0")],
              foreground=[("disabled", "#EFEFEF")])

    style.configure("Secundario.TButton",
                    background=COL_PANEL, foreground=COL_TEXTO,
                    font=FONT_BASE, borderwidth=1, relief="solid",
                    padding=(10, 6))
    style.map("Secundario.TButton",
              background=[("active", "#EFEFEF"), ("disabled", "#F5F5F5")],
              foreground=[("disabled", "#A0A0A0")])

    style.configure("TCheckbutton", background=COL_PANEL,
                    foreground=COL_TEXTO, font=FONT_BASE)
    style.map("TCheckbutton", background=[("active", COL_PANEL)])

    style.configure("Horizontal.TProgressbar",
                    troughcolor="#E5E5E5", background=COL_ACENTO,
                    bordercolor=COL_BORDE, lightcolor=COL_ACENTO,
                    darkcolor=COL_ACENTO, thickness=8)

    style.configure("TEntry", fieldbackground="white", bordercolor=COL_BORDE,
                    lightcolor=COL_BORDE, darkcolor=COL_BORDE, padding=4)

    style.configure("Treeview",
                    background=COL_PANEL, fieldbackground=COL_PANEL,
                    foreground=COL_TEXTO, rowheight=26, font=FONT_BASE,
                    bordercolor=COL_BORDE, borderwidth=1)
    style.configure("Treeview.Heading",
                    background="#FAFAFA", foreground=COL_TEXTO,
                    font=FONT_BOLD, relief="flat", padding=6)
    style.map("Treeview",
              background=[("selected", COL_ACENTO)],
              foreground=[("selected", "white")])


# =====================================================================
#  Ventana: Configuración general
# =====================================================================
class EditorGeneral(tk.Toplevel):
    def __init__(self, parent, config_data, on_save):
        super().__init__(parent)
        self.title(f"{APP_NOMBRE} — Configuración general")
        self.geometry("680x280")
        self.resizable(False, False)
        self.configure(bg=COL_FONDO)
        self.transient(parent)
        self.grab_set()

        self.config_data = config_data
        self.on_save = on_save
        self._construir_ui()

    def _construir_ui(self):
        header = ttk.Frame(self, style="TFrame")
        header.pack(fill="x", padx=20, pady=(15, 5))
        ttk.Label(header, text="Configuración general",
                  style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(header, text="Define las rutas principales del sistema",
                  style="Subtitulo.TLabel").pack(anchor="w")

        card = tk.Frame(self, bg=COL_PANEL, highlightbackground=COL_BORDE,
                        highlightthickness=1)
        card.pack(fill="both", expand=True, padx=20, pady=15)

        ttk.Label(card, text="Carpeta Origen:", style="Card.TLabel").grid(
            row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        self.entry_origen = ttk.Entry(card, width=60)
        self.entry_origen.grid(row=0, column=1, padx=5, pady=(15, 5), sticky="ew")
        self.entry_origen.insert(0, self.config_data.get("origen", ""))
        ttk.Button(card, text="Examinar…", style="Secundario.TButton",
                   command=self._elegir_origen).grid(row=0, column=2, padx=10, pady=(15, 5))

        ttk.Label(card, text="Carpeta de Logs:", style="Card.TLabel").grid(
            row=1, column=0, sticky="w", padx=15, pady=5)
        self.entry_logs = ttk.Entry(card, width=60)
        self.entry_logs.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.entry_logs.insert(0, self.config_data.get("log_dir", ""))
        ttk.Button(card, text="Examinar…", style="Secundario.TButton",
                   command=self._elegir_logs).grid(row=1, column=2, padx=10, pady=5)

        ttk.Label(card, text="Ejemplo Origen:  D:\\Archivos Lectra",
                  style="Secundario.TLabel").grid(row=2, column=1, sticky="w", padx=5)
        ttk.Label(card, text="Ejemplo Logs:    C:\\FileSync-S1\\Logs",
                  style="Secundario.TLabel").grid(row=3, column=1, sticky="w", padx=5)

        card.columnconfigure(1, weight=1)

        botones = ttk.Frame(self, style="TFrame")
        botones.pack(fill="x", padx=20, pady=(0, 15))

        ttk.Button(botones, text="Cancelar", style="Secundario.TButton",
                   command=self.destroy).pack(side="right", padx=5)
        ttk.Button(botones, text="Guardar", style="Acento.TButton",
                   command=self._guardar).pack(side="right", padx=5)

    def _elegir_origen(self):
        ruta = filedialog.askdirectory(title="Selecciona la carpeta Origen")
        if ruta:
            self.entry_origen.delete(0, "end")
            self.entry_origen.insert(0, ruta)

    def _elegir_logs(self):
        ruta = filedialog.askdirectory(title="Selecciona la carpeta de Logs")
        if ruta:
            self.entry_logs.delete(0, "end")
            self.entry_logs.insert(0, ruta)

    def _guardar(self):
        origen = self.entry_origen.get().strip()
        logs = self.entry_logs.get().strip()

        if not origen or not logs:
            messagebox.showwarning("Faltan datos", "Completa Origen y carpeta de Logs.")
            return

        if not os.path.exists(origen):
            if not messagebox.askyesno(
                "Origen no existe",
                f"La carpeta Origen no existe actualmente:\n{origen}\n\n"
                "¿Guardar de todas formas?"
            ):
                return

        self.config_data["origen"] = origen
        self.config_data["log_dir"] = logs

        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error al guardar", str(e))
            return

        messagebox.showinfo("Guardado", "Configuración general actualizada.")
        self.on_save()
        self.destroy()


# =====================================================================
#  Ventana: Administrador de cortadoras
# =====================================================================
class EditorCortadoras(tk.Toplevel):
    def __init__(self, parent, config_data, on_save):
        super().__init__(parent)
        self.title(f"{APP_NOMBRE} — Administrar cortadoras")
        self.geometry("720x520")
        self.resizable(False, False)
        self.configure(bg=COL_FONDO)
        self.transient(parent)
        self.grab_set()

        self.config_data = config_data
        self.on_save = on_save
        self._construir_ui()
        self._cargar_tabla()

    def _construir_ui(self):
        header = ttk.Frame(self, style="TFrame")
        header.pack(fill="x", padx=20, pady=(15, 5))
        ttk.Label(header, text="Administrar cortadoras",
                  style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(header, text="Agrega, edita o elimina destinos de replicación",
                  style="Subtitulo.TLabel").pack(anchor="w")

        card = tk.Frame(self, bg=COL_PANEL, highlightbackground=COL_BORDE,
                        highlightthickness=1)
        card.pack(fill="both", expand=True, padx=20, pady=10)

        columnas = ("nombre", "host", "ruta")
        self.tree = ttk.Treeview(card, columns=columnas, show="headings", height=8)
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("host",   text="Dirección IP")
        self.tree.heading("ruta",   text="Ruta UNC")
        self.tree.column("nombre", width=140)
        self.tree.column("host",   width=140)
        self.tree.column("ruta",   width=380)
        self.tree.pack(fill="both", expand=True, side="left", padx=(10, 0), pady=10)

        scroll = ttk.Scrollbar(card, orient="vertical", command=self.tree.yview)
        scroll.pack(side="right", fill="y", padx=(0, 10), pady=10)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.bind("<Double-1>", lambda e: self._cargar_en_form())

        form = tk.Frame(self, bg=COL_PANEL, highlightbackground=COL_BORDE,
                        highlightthickness=1)
        form.pack(fill="x", padx=20, pady=5)

        ttk.Label(form, text="Nombre:", style="Card.TLabel").grid(
            row=0, column=0, sticky="w", padx=(15, 5), pady=(12, 5))
        self.entry_nombre = ttk.Entry(form, width=22)
        self.entry_nombre.grid(row=0, column=1, sticky="w", padx=5, pady=(12, 5))

        ttk.Label(form, text="IP:", style="Card.TLabel").grid(
            row=0, column=2, sticky="w", padx=(15, 5), pady=(12, 5))
        self.entry_ip = ttk.Entry(form, width=18)
        self.entry_ip.grid(row=0, column=3, sticky="w", padx=5, pady=(12, 5))

        ttk.Label(form, text="Nombre del share:", style="Card.TLabel").grid(
            row=1, column=0, sticky="w", padx=(15, 5), pady=(5, 12))
        self.entry_share = ttk.Entry(form, width=22)
        self.entry_share.grid(row=1, column=1, sticky="w", padx=5, pady=(5, 12))
        self.entry_share.insert(0, "CORTADORA_MARKERS")

        ttk.Label(form, text="(ej: CORTADORA3_MARKERS)",
                  style="Secundario.TLabel").grid(
            row=1, column=2, columnspan=2, sticky="w", padx=5, pady=(5, 12))

        botones = ttk.Frame(self, style="TFrame")
        botones.pack(fill="x", padx=20, pady=(10, 15))

        ttk.Button(botones, text="Agregar", style="Secundario.TButton",
                   command=self._agregar).pack(side="left", padx=3)
        ttk.Button(botones, text="Editar", style="Secundario.TButton",
                   command=self._editar).pack(side="left", padx=3)
        ttk.Button(botones, text="Eliminar", style="Secundario.TButton",
                   command=self._eliminar).pack(side="left", padx=3)

        ttk.Button(botones, text="Cancelar", style="Secundario.TButton",
                   command=self.destroy).pack(side="right", padx=3)
        ttk.Button(botones, text="Guardar cambios", style="Acento.TButton",
                   command=self._guardar).pack(side="right", padx=3)

    def _cargar_tabla(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for c in self.config_data["cortadoras"]:
            self.tree.insert("", "end", values=(c["nombre"], c["host"], c["ruta"]))

    def _cargar_en_form(self):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        self.entry_nombre.delete(0, "end")
        self.entry_nombre.insert(0, vals[0])
        self.entry_ip.delete(0, "end")
        self.entry_ip.insert(0, vals[1])
        ruta = vals[2]
        share = ruta.split("\\")[-1] if "\\" in ruta else ""
        self.entry_share.delete(0, "end")
        self.entry_share.insert(0, share)

    def _validar(self):
        nombre = self.entry_nombre.get().strip()
        ip = self.entry_ip.get().strip()
        share = self.entry_share.get().strip()

        if not nombre or not ip or not share:
            messagebox.showwarning("Faltan datos",
                                   "Completa nombre, IP y nombre del share.")
            return None

        partes = ip.split(".")
        if len(partes) != 4 or not all(p.isdigit() and 0 <= int(p) <= 255 for p in partes):
            messagebox.showerror("IP inválida", f"'{ip}' no es una IP válida.")
            return None

        return {"nombre": nombre, "host": ip, "ruta": f"\\\\{ip}\\{share}"}

    def _agregar(self):
        datos = self._validar()
        if not datos:
            return
        if any(c["host"] == datos["host"] for c in self.config_data["cortadoras"]):
            messagebox.showerror("Duplicado",
                                 f"Ya existe una cortadora con IP {datos['host']}.")
            return
        self.config_data["cortadoras"].append(datos)
        self._cargar_tabla()
        self._limpiar_form()

    def _editar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Selecciona", "Elige una cortadora de la lista.")
            return
        idx = self.tree.index(sel[0])
        datos = self._validar()
        if not datos:
            return
        for i, c in enumerate(self.config_data["cortadoras"]):
            if i != idx and c["host"] == datos["host"]:
                messagebox.showerror("Duplicado",
                                     f"Ya existe otra cortadora con IP {datos['host']}.")
                return
        self.config_data["cortadoras"][idx] = datos
        self._cargar_tabla()
        self._limpiar_form()

    def _eliminar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Selecciona", "Elige una cortadora de la lista.")
            return
        idx = self.tree.index(sel[0])
        nombre = self.config_data["cortadoras"][idx]["nombre"]
        if not messagebox.askyesno("Confirmar", f"¿Eliminar '{nombre}'?"):
            return
        del self.config_data["cortadoras"][idx]
        self._cargar_tabla()
        self._limpiar_form()

    def _limpiar_form(self):
        self.entry_nombre.delete(0, "end")
        self.entry_ip.delete(0, "end")
        self.entry_share.delete(0, "end")
        self.entry_share.insert(0, "CORTADORA_MARKERS")

    def _guardar(self):
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error al guardar", str(e))
            return
        messagebox.showinfo("Guardado", "Cortadoras actualizadas.")
        self.on_save()
        self.destroy()


# =====================================================================
#  Ventana principal
# =====================================================================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITULO)
        self.geometry("1000x820")
        self.minsize(900, 720)
        self.configure(bg=COL_FONDO)

        aplicar_estilos(self)

        self.config_data = self._cargar_config()
        self.vars_cortadoras = {}
        self.replicando = False

        self._construir_ui()
        self._poner_icono()

    # -----------------------------------------------------------------
    def _poner_icono(self):
        try:
            self._ico = crear_icono_pc()
            self.iconphoto(True, self._ico)
        except Exception:
            pass

    # -----------------------------------------------------------------
    def _cargar_config(self):
        if not CONFIG_PATH.exists():
            messagebox.showerror("Config", f"No se encontró:\n{CONFIG_PATH}")
            self.destroy()
            raise SystemExit
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    # -----------------------------------------------------------------
    def _construir_ui(self):
        # ============ HEADER ============
        header = tk.Frame(self, bg=COL_ACENTO, height=64)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="PD-FileSync",
                 bg=COL_ACENTO, fg="white",
                 font=("Segoe UI Semibold", 16)).pack(side="left", padx=(20, 8), pady=12)
        tk.Label(header, text=f"v{VERSION}",
                 bg=COL_ACENTO, fg="#CFE3F5",
                 font=("Segoe UI", 9)).pack(side="left", pady=(20, 12))
        tk.Label(header, text="Sistema de respaldos automático · Servidor 1 → Cortadoras",
                 bg=COL_ACENTO, fg="#E8F1FB",
                 font=("Segoe UI", 10)).pack(side="left", padx=20, pady=12)

        tk.Label(header, text="© 2026 Pro Dept · Designed & Developed by PD-IT-MH",
                 bg=COL_ACENTO, fg="#CFE3F5",
                 font=("Segoe UI", 8)).pack(side="right", padx=20, pady=12)

        cuerpo = ttk.Frame(self, style="TFrame")
        cuerpo.pack(fill="both", expand=True, padx=16, pady=12)

        # ----- Card: Configuración actual -----
        card_cfg = tk.Frame(cuerpo, bg=COL_PANEL, highlightbackground=COL_BORDE,
                            highlightthickness=1)
        card_cfg.pack(fill="x", pady=(0, 10))

        self.frame_cfg_inner = tk.Frame(card_cfg, bg=COL_PANEL)
        self.frame_cfg_inner.pack(fill="x", padx=16, pady=12)
        self._render_cabecera()

        # ----- Card: Cortadoras -----
        card_cort = tk.Frame(cuerpo, bg=COL_PANEL, highlightbackground=COL_BORDE,
                             highlightthickness=1)
        card_cort.pack(fill="x", pady=(0, 10))

        tk.Label(card_cort, text="Cortadoras a replicar",
                 bg=COL_PANEL, fg=COL_TEXTO,
                 font=FONT_BOLD).pack(anchor="w", padx=16, pady=(12, 4))

        self.frame_cort = tk.Frame(card_cort, bg=COL_PANEL)
        self.frame_cort.pack(fill="x", padx=16, pady=(0, 12))
        self._render_cortadoras()

        # ----- Barra de acciones -----
        barra = tk.Frame(cuerpo, bg=COL_FONDO)
        barra.pack(fill="x", pady=(0, 10))

        self.btn_replicar = ttk.Button(barra, text="▶  Replicar ahora",
                                       style="Acento.TButton",
                                       command=self._on_replicar)
        self.btn_replicar.pack(side="left")

        self.btn_config_general = ttk.Button(barra, text="Configuración general",
                                             style="Secundario.TButton",
                                             command=self._abrir_editor_general)
        self.btn_config_general.pack(side="left", padx=8)

        self.btn_admin_cortadoras = ttk.Button(barra, text="Administrar cortadoras",
                                               style="Secundario.TButton",
                                               command=self._abrir_editor)
        self.btn_admin_cortadoras.pack(side="left")

        self.btn_abrir_logs = ttk.Button(barra, text="Abrir carpeta de logs",
                                         style="Secundario.TButton",
                                         command=self._abrir_logs)
        self.btn_abrir_logs.pack(side="left", padx=8)

        self.btn_acerca_de = ttk.Button(barra, text="ℹ  Acerca de",
                                        style="Secundario.TButton",
                                        command=self._abrir_acerca_de)
        self.btn_acerca_de.pack(side="left")

        self.btn_salir = ttk.Button(barra, text="Salir",
                                    style="Secundario.TButton",
                                    command=self.destroy)
        self.btn_salir.pack(side="right")

        # ----- Panel de progreso en vivo -----
        card_prog = tk.Frame(cuerpo, bg=COL_PANEL, highlightbackground=COL_BORDE,
                             highlightthickness=1)
        card_prog.pack(fill="x", pady=(0, 10))

        prog_inner = tk.Frame(card_prog, bg=COL_PANEL)
        prog_inner.pack(fill="x", padx=16, pady=10)

        fila1 = tk.Frame(prog_inner, bg=COL_PANEL)
        fila1.pack(fill="x")

        self.lbl_prog_titulo = tk.Label(
            fila1, text="Listo para replicar",
            bg=COL_PANEL, fg=COL_TEXTO,
            font=("Segoe UI Semibold", 11), anchor="w")
        self.lbl_prog_titulo.pack(side="left")

        self.lbl_prog_pct = tk.Label(
            fila1, text="0%",
            bg=COL_PANEL, fg=COL_ACENTO,
            font=("Segoe UI Semibold", 14), anchor="e")
        self.lbl_prog_pct.pack(side="right")

        self.lbl_prog_archivo = tk.Label(
            prog_inner, text="",
            bg=COL_PANEL, fg=COL_TEXTO_SEC,
            font=("Segoe UI", 9), anchor="w")
        self.lbl_prog_archivo.pack(fill="x", pady=(2, 6))

        self.progress = ttk.Progressbar(prog_inner, mode="determinate",
                                        style="Horizontal.TProgressbar",
                                        maximum=100)
        self.progress.pack(fill="x")

        # ----- Consola -----
        card_consola = tk.Frame(cuerpo, bg=COL_PANEL, highlightbackground=COL_BORDE,
                                highlightthickness=1)
        card_consola.pack(fill="both", expand=True)

        tk.Label(card_consola, text="Salida en vivo",
                 bg=COL_PANEL, fg=COL_TEXTO,
                 font=FONT_BOLD).pack(anchor="w", padx=16, pady=(12, 6))

        self.txt_log = scrolledtext.ScrolledText(
            card_consola, wrap="word",
            bg=COL_CONSOLE_BG, fg=COL_CONSOLE_FG,
            insertbackground="white",
            font=FONT_CONSOLA, relief="flat", borderwidth=0,
            padx=10, pady=8,
        )
        self.txt_log.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.txt_log.tag_config("info",   foreground=COL_CONSOLE_INFO)
        self.txt_log.tag_config("ok",     foreground=COL_CONSOLE_OK)
        self.txt_log.tag_config("warn",   foreground=COL_CONSOLE_WARN)
        self.txt_log.tag_config("err",    foreground=COL_CONSOLE_ERR)
        self.txt_log.tag_config("header", foreground="white",
                                font=("Consolas", 9, "bold"))
        self.txt_log.tag_config("sep",    foreground="#555555")
        self.txt_log.tag_config("sub",    foreground="#C586C0",
                                font=("Consolas", 9, "bold"))

    # -----------------------------------------------------------------
    def _render_cabecera(self):
        for w in self.frame_cfg_inner.winfo_children():
            w.destroy()

        tk.Label(self.frame_cfg_inner, text="Origen:",
                 bg=COL_PANEL, fg=COL_TEXTO_SEC,
                 font=FONT_BOLD).grid(row=0, column=0, sticky="w", pady=3)
        tk.Label(self.frame_cfg_inner, text=self.config_data.get("origen", ""),
                 bg=COL_PANEL, fg=COL_TEXTO,
                 font=FONT_BASE).grid(row=0, column=1, sticky="w", padx=(10, 0))

        tk.Label(self.frame_cfg_inner, text="Logs:",
                 bg=COL_PANEL, fg=COL_TEXTO_SEC,
                 font=FONT_BOLD).grid(row=1, column=0, sticky="w", pady=3)
        tk.Label(self.frame_cfg_inner, text=self.config_data.get("log_dir", ""),
                 bg=COL_PANEL, fg=COL_TEXTO,
                 font=FONT_BASE).grid(row=1, column=1, sticky="w", padx=(10, 0))

    # -----------------------------------------------------------------
    def _render_cortadoras(self):
        for w in self.frame_cort.winfo_children():
            w.destroy()
        self.vars_cortadoras.clear()

        for i, c in enumerate(self.config_data["cortadoras"]):
            var = tk.BooleanVar(value=True)
            self.vars_cortadoras[c["nombre"]] = var
            chk = ttk.Checkbutton(
                self.frame_cort,
                text=f"{c['nombre']}  ({c['host']})",
                variable=var,
                style="TCheckbutton",
            )
            chk.grid(row=i // 4, column=i % 4, padx=(0, 20), pady=3, sticky="w")

    # -----------------------------------------------------------------
    def _abrir_editor(self):
        EditorCortadoras(self, self.config_data, on_save=self._recargar_config)

    def _abrir_editor_general(self):
        EditorGeneral(self, self.config_data, on_save=self._recargar_config)

    def _recargar_config(self):
        self.config_data = self._cargar_config()
        self._render_cabecera()
        self._render_cortadoras()

    # -----------------------------------------------------------------
    def _log(self, texto, tag=None):
        if tag:
            self.txt_log.insert("end", texto + "\n", tag)
        else:
            self.txt_log.insert("end", texto + "\n")
        self.txt_log.see("end")
        self.update_idletasks()

    def _log_sep(self, char="─", n=80):
        self._log(char * n, "sep")

    # -----------------------------------------------------------------
    def _bloquear_botones(self):
        self.btn_replicar.config(state="disabled")
        self.btn_config_general.config(state="disabled")
        self.btn_admin_cortadoras.config(state="disabled")
        self.btn_salir.config(state="disabled")

    def _desbloquear_botones(self):
        self.btn_replicar.config(state="normal")
        self.btn_config_general.config(state="normal")
        self.btn_admin_cortadoras.config(state="normal")
        self.btn_salir.config(state="normal")

    # -----------------------------------------------------------------
    def _on_replicar(self):
        if self.replicando:
            messagebox.showinfo("En curso", "Ya hay una replicación en curso.")
            return

        seleccionadas = [c for c in self.config_data["cortadoras"]
                         if self.vars_cortadoras.get(c["nombre"]) and
                            self.vars_cortadoras[c["nombre"]].get()]

        if not seleccionadas:
            messagebox.showwarning("Sin selección", "Marca al menos una cortadora.")
            return

        if not messagebox.askyesno("Confirmar",
                                    f"¿Replicar hacia {len(seleccionadas)} cortadora(s)?"):
            return

        self.replicando = True
        self._bloquear_botones()
        self.txt_log.delete("1.0", "end")
        self.progress["value"] = 0

        hilo = threading.Thread(target=self._ejecutar_replicacion,
                                args=(seleccionadas,), daemon=True)
        hilo.start()

    # -----------------------------------------------------------------
    def _get_usuario(self):
        try:
            dom = os.environ.get("USERDOMAIN", "")
            usr = os.environ.get("USERNAME", "") or os.getlogin()
            if dom:
                return f"{dom}\\{usr}"
            return usr
        except Exception:
            return "N/A"

    # -----------------------------------------------------------------
    def _formato_fecha_larga(self, dt: datetime) -> str:
        dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
                 "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        return f"{dias[dt.weekday()]}, {dt.day} de {meses[dt.month - 1]} de {dt.year} {dt.strftime('%H:%M:%S')}"

    # -----------------------------------------------------------------
    def _actualizar_progreso(self, nombre_cortadora: str, idx: int, total_cort: int,
                             procesados: int, total: int, archivo: str):
        """Callback desde el hilo. Actualiza la barra basándose en archivos."""
        if total <= 0:
            return
        pct = min(100, int((procesados / total) * 100))

        # Acortar la ruta del archivo para que no rompa el layout
        arch_corto = archivo
        if len(archivo) > 70:
            arch_corto = "…" + archivo[-68:]

        def _update():
            try:
                self.lbl_prog_titulo.config(
                    text=f"Replicando [{idx}/{total_cort}]: {nombre_cortadora}")
                self.lbl_prog_pct.config(text=f"{pct}%")
                self.lbl_prog_archivo.config(
                    text=f"{arch_corto}   ·   {procesados:,} / {total:,} archivos")
                self.progress["value"] = pct
            except Exception:
                pass

        try:
            self.after(0, _update)
        except Exception:
            pass

    # -----------------------------------------------------------------
    def _ejecutar_replicacion(self, cortadoras):
        resumen = []
        usuario = self._get_usuario()
        inicio_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        inicio_largo = self._formato_fecha_larga(datetime.now())
        total_cort = len(cortadoras)

        # --- Encabezado ---
        self._log_sep("═")
        self._log(f"  {APP_NOMBRE}  ·  INICIO {inicio_iso}", "header")
        self._log_sep("═")
        self._log(f"Iniciado : {inicio_largo}")
        self._log(f"Usuario  : {usuario}", "info")
        self._log(f"Origen   : {self.config_data['origen']}", "info")
        self._log(f"Destinos : {total_cort} cortadora(s)")
        for c in cortadoras:
            self._log(f"            • {c['nombre']}  →  {c['ruta']}", "info")
        self._log("")

        # --- Procesando ---
        self._log_sep("─")
        self._log("  PROCESANDO CORTADORAS", "sub")
        self._log_sep("─")
        self._log("")

        errores_detalle = []

        for idx, c in enumerate(cortadoras, start=1):
            self.after(0, lambda i=idx, n=c['nombre'], t=total_cort: (
                self.lbl_prog_titulo.config(text=f"Replicando [{i}/{t}]: {n}"),
                self.lbl_prog_pct.config(text="0%"),
                self.lbl_prog_archivo.config(text="Contando archivos de origen…"),
                self.progress.config(value=0),
            ))

            rep = Replicador(
                origen=self.config_data["origen"],
                destino=c["ruta"],
                log_dir=self.config_data["log_dir"],
                nombre_cortadora=c["nombre"],
            )

            errores_cortadora = []

            def _cb(linea):
                l_s = linea.strip()
                if ("ERROR 32" in l_s or "ERROR 5" in l_s
                        or "denied" in l_s.lower() or "denegado" in l_s.lower()
                        or "being used" in l_s.lower()
                        or "utilizado por otro" in l_s.lower()):
                    errores_cortadora.append(l_s)

            def _cb_prog(procesados, total, archivo, _idx=idx, _nom=c["nombre"]):
                self._actualizar_progreso(_nom, _idx, total_cort, procesados, total, archivo)

            res = rep.ejecutar(callback_linea=_cb, callback_progreso=_cb_prog)

            self.after(0, lambda n=c['nombre']: (
                self.lbl_prog_titulo.config(text=f"✓ {n} completada"),
                self.lbl_prog_pct.config(text="100%"),
                self.lbl_prog_archivo.config(text=""),
                self.progress.config(value=100),
            ))

            copiados = res.get("copiados", 0)
            errores = res.get("errores", 0)
            ya_sinc = res.get("ya_sincronizados", 0)
            estado_txt = res["estado"]

            if errores == 0:
                icono = "✓"
                tag_estado = "ok"
            elif errores < copiados:
                icono = "⚠"
                tag_estado = "warn"
            else:
                icono = "✗"
                tag_estado = "err"

            self._log(f"  [{idx}/{total_cort}]  {c['nombre']}  →  {c['ruta']}", "sub")
            self._log(
                f"         {icono} {estado_txt}",
                tag_estado
            )
            self._log(f"         ► Copiados         : {copiados:,}")
            self._log(f"         ► Ya sincronizados : {ya_sinc:,}")
            self._log(f"         ► Errores          : {errores}",
                      "err" if errores > 0 else None)
            self._log("")

            if errores_cortadora:
                errores_detalle.append((c["nombre"], errores_cortadora))

            resumen.append(res)
            self.update_idletasks()

        # --- Bloque: DETALLE DE ARCHIVOS REPLICADOS ---
        total_copiados = sum(r.get("copiados", 0) for r in resumen)
        total_errores  = sum(r.get("errores", 0) for r in resumen)
        total_ya_sinc  = sum(r.get("ya_sincronizados", 0) for r in resumen)

        self._log_sep("─")
        self._log("  DETALLE DE ARCHIVOS REPLICADOS", "sub")
        self._log_sep("─")
        self._log(f"  {'':<18}{'Tamaño':>10}    Ruta-Servidor")

        archivos_vistos = set()
        total_archivos_unicos = 0

        for r in resumen:
            for linea in r.get("nuevos", []):
                texto = linea.strip()

                if texto.startswith("Nuevo arch") or texto.startswith("New File"):
                    tipo = "Nuevo archivo"
                elif texto.startswith("Más reciente") or texto.startswith("Newer"):
                    tipo = "Modificado"
                else:
                    continue

                tamano = "?"
                ruta = ""
                try:
                    resto = texto
                    for pref in ("Nuevo archivo", "Nuevo arch",
                                 "New File", "Más reciente", "Newer"):
                        if resto.startswith(pref):
                            resto = resto[len(pref):].lstrip()
                            break
                    sub = resto.split(None, 1)
                    if len(sub) >= 2:
                        tamano = sub[0]
                        ruta = sub[1].strip()
                except Exception:
                    pass

                if ruta and ruta not in archivos_vistos:
                    archivos_vistos.add(ruta)
                    total_archivos_unicos += 1

                    try:
                        bytes_val = int(tamano)
                        if bytes_val < 1024:
                            tamano_fmt = f"{bytes_val} B"
                        elif bytes_val < 1024 * 1024:
                            tamano_fmt = f"{bytes_val / 1024:.1f} KB"
                        else:
                            tamano_fmt = f"{bytes_val / (1024 * 1024):.1f} MB"
                    except Exception:
                        tamano_fmt = tamano

                    self._log(f"  {tipo:<18}{tamano_fmt:>10}    {ruta}")

        if total_archivos_unicos == 0:
            self._log("  (No hubo archivos nuevos o modificados en esta ejecución)")
        self._log("")

        # --- Errores ---
        if errores_detalle:
            self._log_sep("─")
            self._log("  ⚠ ARCHIVOS CON PROBLEMAS", "err")
            self._log_sep("─")
            for nombre_cort, errs in errores_detalle:
                self._log(f"  • {nombre_cort}:", "warn")
                for e in errs[:10]:
                    self._log(f"      - {e.strip()}", "err")
                if len(errs) > 10:
                    self._log(f"      ... y {len(errs) - 10} más (ver log)", "warn")
            self._log("")

        # --- Tabla final ---
        self._log_sep("═")
        self._log("  RESUMEN FINAL", "header")
        self._log_sep("═")
        self._log(
            f"  {'CORTADORA':<22}"
            f"{'ESTADO':<28}"
            f"{'COPIADOS':>10}"
            f"{'YA SINCR.':>12}"
            f"{'ERRORES':>10}"
        )
        for r in resumen:
            nombre = r["cortadora"][:20]
            estado = r["estado"][:26]
            cop = r.get("copiados", 0)
            sinc = r.get("ya_sincronizados", 0)
            err = r.get("errores", 0)
            linea = (f"  {nombre:<22}{estado:<28}"
                     f"{cop:>10}{sinc:>12}{err:>10}")
            self._log(linea, "err" if err > 0 else "ok")

        if len(resumen) > 1:
            self._log_sep("─")
            linea_tot = (
                f"  {'TOTAL':<22}{'':<28}"
                f"{total_copiados:>10}{total_ya_sinc:>12}{total_errores:>10}"
            )
            self._log(linea_tot, "err" if total_errores > 0 else "ok")

        self._log_sep("═")
        self._log(f"  Logs: {self.config_data['log_dir']}", "info")
        self._log(f"  Fin : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "info")
        self._log_sep("═")
        self._log(f"  {COPYRIGHT}", "info")
        self._log(f"  {CREDITOS}", "info")
        self._log_sep("═")

        # Reset panel de progreso
        self.after(0, lambda: (
            self.lbl_prog_titulo.config(text="Listo para replicar"),
            self.lbl_prog_pct.config(text="0%"),
            self.lbl_prog_archivo.config(text=""),
            self.progress.config(value=0),
        ))

        self.replicando = False
        self._desbloquear_botones()

        messagebox.showinfo(f"{APP_NOMBRE}",
                            "Replicación completada. Revisa los logs.")

    # -----------------------------------------------------------------
    def _abrir_logs(self):
        ruta = self.config_data["log_dir"]
        if os.path.exists(ruta):
            os.startfile(ruta)
        else:
            messagebox.showwarning("No existe", f"No existe la carpeta:\n{ruta}")

    # -----------------------------------------------------------------
    def _abrir_acerca_de(self):
        dlg = tk.Toplevel(self)
        dlg.title(f"Acerca de {APP_NOMBRE}")
        dlg.geometry("560x380")
        dlg.resizable(False, False)
        dlg.configure(bg=COL_FONDO)
        dlg.transient(self)
        dlg.grab_set()

        header = tk.Frame(dlg, bg=COL_ACENTO, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="PD-FileSync",
                 bg=COL_ACENTO, fg="white",
                 font=("Segoe UI Semibold", 20)).pack(anchor="w", padx=24, pady=(14, 0))
        tk.Label(header, text=f"Versión {VERSION}",
                 bg=COL_ACENTO, fg="#CFE3F5",
                 font=("Segoe UI", 10)).pack(anchor="w", padx=24)

        body = tk.Frame(dlg, bg=COL_FONDO)
        body.pack(fill="both", expand=True, padx=24, pady=20)

        tk.Label(body, text="Sistema de respaldos automático de archivos",
                 bg=COL_FONDO, fg=COL_TEXTO,
                 font=("Segoe UI Semibold", 12),
                 anchor="w", justify="left").pack(fill="x", pady=(0, 4))

        tk.Label(body, text="Réplica en tiempo real desde el Servidor1 hacia las cortadoras (espejo)",
                 bg=COL_FONDO, fg=COL_TEXTO_SEC,
                 font=("Segoe UI", 10),
                 anchor="w", justify="left").pack(fill="x", pady=(0, 16))

        info_frame = tk.Frame(body, bg=COL_PANEL,
                              highlightbackground=COL_BORDE, highlightthickness=1)
        info_frame.pack(fill="x", pady=(0, 16))

        lineas = [
            ("Aplicación:", f"{APP_NOMBRE}"),
            ("Versión:", VERSION),
            ("Tipo:", "Herramienta de respaldo / sincronización"),
            ("Destinos:", "Servidor1 → Cortadoras Lectra"),
        ]
        for i, (k, v) in enumerate(lineas):
            tk.Label(info_frame, text=k, bg=COL_PANEL, fg=COL_TEXTO_SEC,
                     font=FONT_BOLD, anchor="w").grid(row=i, column=0,
                                                       sticky="w", padx=12, pady=3)
            tk.Label(info_frame, text=v, bg=COL_PANEL, fg=COL_TEXTO,
                     font=FONT_BASE, anchor="w").grid(row=i, column=1,
                                                       sticky="w", padx=12, pady=3)

        tk.Label(body, text=COPYRIGHT,
                 bg=COL_FONDO, fg=COL_TEXTO_SEC,
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 2))
        tk.Label(body, text=CREDITOS,
                 bg=COL_FONDO, fg=COL_ACENTO,
                 font=("Segoe UI Semibold", 10)).pack(anchor="w")

        ttk.Button(dlg, text="Cerrar", style="Acento.TButton",
                   command=dlg.destroy).pack(pady=(0, 20))


# =====================================================================
if __name__ == "__main__":
    App().mainloop()