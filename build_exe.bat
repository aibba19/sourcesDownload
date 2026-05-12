@echo off
setlocal

REM Build a standalone Windows executable (no console window)
if not exist .venv\Scripts\python.exe (
  echo [ERRORE] Ambiente virtuale non trovato in .venv
  echo Crea l'ambiente: python -m venv .venv
  exit /b 1
)

.venv\Scripts\python.exe -m pip install --upgrade pip pyinstaller
if errorlevel 1 exit /b 1

.venv\Scripts\pyinstaller.exe --noconfirm --clean --onefile --noconsole --name sourcesDownload app\main.py
if errorlevel 1 exit /b 1

echo.
echo Build completata. Eseguibile disponibile in dist\sourcesDownload.exe
endlocal
