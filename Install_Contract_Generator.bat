@echo off
chcp 65001 >nul
setlocal

set "ZIP_FILE=%~dp0Contract_Generator_Windows.zip"
set "INSTALL_DIR=%LOCALAPPDATA%\Contract_Generator"

echo.
echo Contract Generator Installer
echo ----------------------------
echo.

if not exist "%ZIP_FILE%" (
  echo FEHLER: Contract_Generator_Windows.zip wurde nicht gefunden.
  echo.
  echo Bitte lege diese Datei in denselben Ordner wie diesen Installer:
  echo %ZIP_FILE%
  echo.
  pause
  exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference='Stop';" ^
  "$zip=$env:ZIP_FILE;" ^
  "$installDir=$env:INSTALL_DIR;" ^
  "$tempDir=Join-Path $env:TEMP ('Contract_Generator_install_' + [guid]::NewGuid().ToString());" ^
  "Write-Host 'Installiere Contract Generator...';" ^
  "Stop-Process -Name 'Contract_Generator' -ErrorAction SilentlyContinue;" ^
  "if (Test-Path -LiteralPath $installDir) { Remove-Item -LiteralPath $installDir -Recurse -Force; }" ^
  "New-Item -ItemType Directory -Force -Path $tempDir | Out-Null;" ^
  "Expand-Archive -LiteralPath $zip -DestinationPath $tempDir -Force;" ^
  "$sourceDir=$tempDir;" ^
  "if (-not (Test-Path -LiteralPath (Join-Path $sourceDir 'Contract_Generator.exe'))) {" ^
  "  $candidate=Get-ChildItem -LiteralPath $tempDir -Directory | Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'Contract_Generator.exe') } | Select-Object -First 1;" ^
  "  if ($candidate) { $sourceDir=$candidate.FullName } else { throw 'Contract_Generator.exe wurde im ZIP nicht gefunden.' }" ^
  "}" ^
  "New-Item -ItemType Directory -Force -Path $installDir | Out-Null;" ^
  "Copy-Item -Path (Join-Path $sourceDir '*') -Destination $installDir -Recurse -Force;" ^
  "Remove-Item -LiteralPath $tempDir -Recurse -Force;" ^
  "$desktop=[Environment]::GetFolderPath('Desktop');" ^
  "$shortcutPath=Join-Path $desktop 'Contract_Generator.lnk';" ^
  "$targetPath=Join-Path $installDir 'Contract_Generator.exe';" ^
  "$shell=New-Object -ComObject WScript.Shell;" ^
  "$shortcut=$shell.CreateShortcut($shortcutPath);" ^
  "$shortcut.TargetPath=$targetPath;" ^
  "$shortcut.WorkingDirectory=$installDir;" ^
  "$shortcut.Description='Contract Generator starten';" ^
  "$shortcut.Save();" ^
  "Write-Host 'Installation abgeschlossen.';" ^
  "Write-Host ('Installationsordner: ' + $installDir);" ^
  "Write-Host ('Desktop-VerknÃ¼pfung: ' + $shortcutPath);"

if errorlevel 1 (
  echo.
  echo Installation fehlgeschlagen.
  echo Bitte prÃ¼fe, ob Contract_Generator.exe noch geÃ¶ffnet ist, und starte den Installer erneut.
  echo.
  pause
  exit /b 1
)

echo.
echo Fertig. Auf dem Desktop liegt jetzt die VerknÃ¼pfung "Contract_Generator".
echo.
pause
