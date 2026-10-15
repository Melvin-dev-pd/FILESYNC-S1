# PD-FileSync_V1.0

Sistema de respaldos tiempo real para redes, servidores, pc, recursos compartidos.(modo espejo).

![Versión](https://img.shields.io/badge/version-1.0-blue)
![Python](https://img.shields.io/badge/python-3.14-blue)
![Plataforma](https://img.shields.io/badge/platform-Windows-lightgrey)

---

## 📋 Descripción

PD-FileSync_V1.0 es una aplicación de escritorio (GUI) que sincroniza archivos desde una carpeta origen otros destinos dentro del entorno de sistema windows, manteniendo una réplica exacta (espejo) del contenido.

Está pensada para entornos de producción donde los operadores necesitan replicar archivos de forma rápida y confiable.

---

## ✨ Características

- 🔄 **Réplica espejo** (modo `/MIR`): copia archivos nuevos, actualiza modificados y elimina los que ya no están en el origen.
- 🖥️ **Interfaz gráfica moderna** estilo Windows 11.
- 📊 **Barra de progreso en vivo** basada en archivos procesados.
- 📄 **Reporte detallado** en consola: copiados, ya sincronizados y errores.
- 🗂️ **Log y CSV por ejecución**: cada replicación genera su propio registro.
- ⚙️ **Administración de cortadoras** desde la propia GUI.
- 🔒 **Detección de archivos bloqueados** y reporte automático.
- 📡 **Verificación de conectividad** por ping antes de replicar.

---

## 🚀 Requisitos

- Windows 10 / 11 (64 bits)
- Permisos de lectura en la carpeta origen
- Permisos de escritura en los shares
- PowerShell 5+ (para ping)

---

## 📦 Instalación

### Opción A — Usar el ejecutable (usuarios finales)

1. Copia la carpeta `PD-FileSync_V1.0` al equipo destino.
2. Asegúrate de que contiene:
   - `PD-FileSync_V1.0.exe`
   - `config.json` (renombra el config.example.json a config.json)
3. Doble clic en `PD-FileSync_V1.0.exe`.

### Opción B — Ejecutar desde código fuente (desarrolladores)

```bash
# Clonar el repositorio
git clone https://github.com/Melvin-dev-pd/FILESYNC-S1.git
cd FILESYNC-S1

# Crear entorno virtual
python -m venv .venv
.venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python main.py
```
