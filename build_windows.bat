@echo off
setlocal
cd /d "%~dp0"

python -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --windowed ^
  --name Contract_Generator ^
  src\app.py

if errorlevel 1 (
  echo.
  echo Build fehlgeschlagen.
  pause
  exit /b 1
)

if exist "dist\Contract_Generator\input" rmdir /s /q "dist\Contract_Generator\input"
if exist "dist\Contract_Generator\templates" rmdir /s /q "dist\Contract_Generator\templates"
if not exist "dist\Contract_Generator\output" mkdir "dist\Contract_Generator\output"

xcopy /e /i /y "input" "dist\Contract_Generator\input" >nul
xcopy /e /i /y "templates" "dist\Contract_Generator\templates" >nul

echo.
echo Windows-App erstellt:
echo dist\Contract_Generator\Contract_Generator.exe
echo.
pause
