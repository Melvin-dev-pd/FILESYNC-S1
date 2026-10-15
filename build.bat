@echo off
REM =====================================================
REM  FileSync-S1 - Script de empaquetado a .exe
REM =====================================================
cd /d "%~dp0"

echo.
echo ============================================
echo  Empaquetando FileSync-S1...
echo ============================================
echo.

pyinstaller ^
  --noconfirm ^
  --onefile ^
  --windowed ^
  --name FileSync-S1 ^
  main.py

echo.
echo ============================================
echo  Empaquetado completado.
echo  Ejecutable en: dist\FileSync-S1.exe
echo ============================================
echo.
echo  NOTA: copia el config.json junto al .exe
echo        para que el programa lo encuentre.
echo ============================================
pause