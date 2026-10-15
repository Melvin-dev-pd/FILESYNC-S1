# =====================================================================
#  PD-FileSync_V1.0 - Motor de replicación (robocopy wrapper)
# =====================================================================
import subprocess
import os
import csv
from datetime import datetime
from pathlib import Path


class Replicador:
    def __init__(self, origen: str, destino: str, log_dir: str, nombre_cortadora: str):
        self.origen = origen
        self.destino = destino
        self.log_dir = Path(log_dir)
        self.nombre = nombre_cortadora
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = f"{self.timestamp}_{nombre_cortadora.replace(' ', '_')}"
        self.log_path = self.log_dir / f"replica_{base}.log"
        self.csv_path = self.log_dir / f"replica_{base}.csv"

    # -----------------------------------------------------------------
    def host_online(self, timeout_ms=1500) -> bool:
        # Si el destino es ruta local (C:\...) no hace ping.
        # Si el destino es UNC (\\IP\share) hace ping a la IP.
        if not self.destino.startswith("\\\\"):
            return True

        host = self.destino.lstrip("\\").split("\\")[0]
        try:
            creation_flags = 0
            if os.name == "nt":
                creation_flags = subprocess.CREATE_NO_WINDOW

            resultado = subprocess.run(
                ["ping", "-n", "1", "-w", str(timeout_ms), host],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=creation_flags,
            )
            
            return resultado.returncode == 0
        except Exception:
            return False

    # -----------------------------------------------------------------
    def _contar_archivos_origen(self) -> int:
        """
        Cuenta los archivos en el origen (recursivo) para estimar el total.
        Ignora errores de permisos y continúa.
        """
        try:
            total = 0
            for _, _, archivos in os.walk(self.origen):
                total += len(archivos)
            return total
        except Exception:
            return 0

    # -----------------------------------------------------------------
    def ejecutar(self, callback_linea=None, callback_progreso=None) -> dict:
        """
        callback_linea: función que recibe cada línea de stdout (para mostrar en GUI).
        callback_progreso: función que recibe (procesados, total, archivo_actual).
        """
        resultado = {
            "cortadora": self.nombre,
            "destino": self.destino,
            "inicio": datetime.now().isoformat(),
            "exit_code": None,
            "estado": "",
            "log": str(self.log_path),
            "csv": str(self.csv_path),
            "nuevos": [],
            "ya_sincronizados": 0,
            "total_archivos": 0,
            "copiados": 0,
            "errores": 0,
        }

        if not self.host_online():
            resultado["estado"] = "SIN CONEXION"
            self._escribir_log_inicial("SIN CONEXION AL HOST")
            return resultado

        if not os.path.exists(self.destino):
            resultado["estado"] = "DESTINO INACCESIBLE"
            self._escribir_log_inicial(f"DESTINO INACCESIBLE: {self.destino}")
            return resultado

        # Contar archivos del origen para estimar el progreso
        total_origen = self._contar_archivos_origen()

        # Comando robocopy (SIN /NP para que emita líneas de progreso)
        cmd = [
            "robocopy", self.origen, self.destino,
            "/MIR", "/FFT", "/R:2", "/W:2",
            "/NDL", "/FP", "/TEE",
            f"/LOG:{self.log_path}",
        ]

        # Variable de estado del progreso
        procesados = 0
        archivo_actual = ""

        def _emitir_progreso(archivo):
            nonlocal procesados, archivo_actual
            procesados += 1
            archivo_actual = archivo
            if callback_progreso:
                callback_progreso(procesados, total_origen, archivo_actual)

                # En Windows, ocultar la ventana de consola del subproceso robocopy.
        # CREATE_NO_WINDOW = 0x08000000
        creation_flags = 0
        if os.name == "nt":
            creation_flags = subprocess.CREATE_NO_WINDOW

        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="cp850",
                errors="replace",
                bufsize=1,
                creationflags=creation_flags,   # ← ESTA ES LA LÍNEA CLAVE
            )

            for linea in proc.stdout:
                linea = linea.rstrip()

                # Detectar archivos copiados → avanzar barra
                l_strip = linea.strip()

                # Formato nuevo (con % al inicio):
                #   100%   Nuevo arch   63155   ruta\archivo
                # Formato viejo (sin %):
                #   Nuevo arch   63155   ruta\archivo
                # También soportamos: Más reciente, New File, Newer
                es_copiado = False
                es_omitido = False
                archivo_linea = ""

                # Quitar prefijo "%" si existe
                l_sin_pct = l_strip
                if l_sin_pct.endswith("%"):
                    l_sin_pct = ""
                elif "%" in l_sin_pct[:6]:
                    # "100%   Nuevo arch..."
                    idx = l_sin_pct.find("%")
                    l_sin_pct = l_sin_pct[idx+1:].lstrip()

                # ¿Es un archivo nuevo/modificado?
                if (l_sin_pct.startswith("Nuevo arch") or
                    l_sin_pct.startswith("New File") or
                    l_sin_pct.startswith("Más reciente") or
                    l_sin_pct.startswith("Newer")):
                    es_copiado = True
                    # Extraer la ruta (última parte después del tamaño)
                    partes = l_sin_pct.split(None, 2)
                    if len(partes) >= 3:
                        archivo_linea = partes[2].strip()

                # ¿Es un archivo omitido (ya sincronizado)?
                # Robocopy NO imprime omitidos individuales con /NDL,
                # así que no los detectamos línea a línea.

                if es_copiado:
                    _emitir_progreso(archivo_linea)

                # Clasificar para el conteo interno
                self._clasificar_linea(linea, resultado)

                # Callback a la GUI para mostrar líneas especiales
                if callback_linea:
                    callback_linea(linea)

            proc.wait()
            resultado["exit_code"] = proc.returncode
            resultado["estado"] = self._interpretar_exit(proc.returncode)
            self._parsear_resumen(resultado)

            # Si procesados < total_origen, significa que robocopy omitió archivos
            # (ya sincronizados). Los contamos como procesados también.
            if total_origen > 0 and procesados < total_origen:
                # No emitimos progreso artificial, solo ajustamos el conteo final
                pass

        except Exception as e:
            resultado["estado"] = f"EXCEPCION: {e}"
            self._escribir_log_inicial(f"EXCEPCION: {e}")

        resultado["fin"] = datetime.now().isoformat()
        self._generar_csv(resultado)
        return resultado

    # -----------------------------------------------------------------
    def _clasificar_linea(self, linea: str, resultado: dict):
        l = linea.strip()

        # Quitar prefijo "%" si existe
        if "%" in l[:6]:
            idx = l.find("%")
            l = l[idx+1:].lstrip()

        marcadores_nuevo = (
            "New File", "Nuevo arch",
            "Newer", "más reciente",
        )
        if any(l.startswith(m) for m in marcadores_nuevo):
            resultado["nuevos"].append(l)
            return

        # Ignorar líneas de resumen
        if (l.startswith("Total") or l.startswith("Director")
                or l.startswith("Archivos") or l.startswith("Bytes")
                or l.startswith("Tiempo") or l.startswith("Finalizado")
                or l.startswith("Files") or l.startswith("Dirs")
                or l.startswith("Times") or l.startswith("Ended")
                or l.startswith("Started") or l.startswith("Speed")
                or l.startswith("Velocidad")):
            return

        palabras_error = (
            "ERROR 32", "ERROR 5",
            "Access is denied",
            "being used by another process",
            "Acceso denegado",
            "está siendo utilizado por otro proceso",
            "The process cannot access",
        )
        if any(p.lower() in l.lower() for p in palabras_error):
            resultado["nuevos"].append("[ERROR] " + l)

    # -----------------------------------------------------------------
    def _parsear_resumen(self, resultado: dict):
        """
        Busca en el log la línea de resumen tipo:
          ' Archivos:         4         4         0         0         0         0'
        Columnas: Total, Copiado, Omitido, Mismatch, ERROR, Extras
        """
        try:
            with open(self.log_path, "r", encoding="cp850", errors="replace") as f:
                for linea in f:
                    l = linea.strip()
                    l_low = l.lower()

                    if not (l_low.startswith("archivos:") or l_low.startswith("files")):
                        continue

                    numeros = [int(t) for t in l.split() if t.isdigit()]
                    if len(numeros) >= 5:
                        resultado["total_archivos"] = numeros[0]
                        resultado["copiados"] = numeros[1]
                        resultado["ya_sincronizados"] = numeros[2]
                        resultado["errores"] = numeros[4]
                        break
        except Exception as e:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(f"\n[PARSER] Error leyendo resumen: {e}\n")

    # -----------------------------------------------------------------
    def _interpretar_exit(self, code: int) -> str:
        if code == 0:
            return "SIN CAMBIOS"
        if code == 1:
            return "REPLICADO SATISFACTORIO"
        if code < 8:
            return "REPLICADO SATISFACTORIO (extras)"
        if code == 8:
            return "REPLICADO PARCIAL - hubo fallos"
        if code >= 16:
            return "ERROR FATAL"
        return f"DESCONOCIDO ({code})"

    # -----------------------------------------------------------------
    def _generar_csv(self, resultado: dict):
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Tipo", "Detalle"])
            for n in resultado["nuevos"]:
                w.writerow(["NUEVO/EDITADO", n])

    # -----------------------------------------------------------------
    def _escribir_log_inicial(self, mensaje: str):
        with open(self.log_path, "w", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] {self.nombre}\n")
            f.write(f"Origen : {self.origen}\n")
            f.write(f"Destino: {self.destino}\n")
            f.write(f"Estado : {mensaje}\n")