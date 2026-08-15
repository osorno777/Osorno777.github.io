@echo off
REM Free C: without git. Run this when "git pull" dies with No space left on device.
setlocal
cd /d "%~dp0"

if not exist E:\ (
  echo Drive E: is not ready.
  exit /b 1
)

mkdir E:\translation_qa\reports 2>nul
mkdir E:\translation_qa\tmp 2>nul
mkdir E:\translation_qa\pycache 2>nul

echo Deleting bulky JSON/CSV copies on C: (HTML reports are kept for resume)...
if exist "%~dp0reports\*.json" del /q "%~dp0reports\*.json"
if exist "%~dp0reports\*.csv" del /q "%~dp0reports\*.csv"

echo Moving remaining reports to E:\translation_qa\reports ...
if exist "%~dp0reports\" (
  robocopy "%~dp0reports" "E:\translation_qa\reports" /E /MOVE /R:1 /W:1
  if errorlevel 8 (
    echo robocopy failed.
    exit /b 1
  )
)
mkdir "%~dp0reports" 2>nul

echo C: should now have room for git pull.
echo Next:
echo   cd %USERPROFILE%\Osorno777.github.io
echo   git pull origin cursor/translation-veracity-checker-5bc6
echo   cd tools\translation_qa
echo   rescan.bat
exit /b 0
