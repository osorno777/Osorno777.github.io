@echo off
setlocal
cd /d "%~dp0"

echo Pulling the latest translation checker...
git -C "%~dp0..\.." pull
if errorlevel 1 (
  echo git pull failed. Stay on this folder and run: git pull
)

copy /Y paths.example.json paths.json >nul
echo.
echo --- Books and translation pairs ---
py -m translation_qa list --config paths.json
if errorlevel 1 (
  echo.
  echo list failed. Fix paths.json or filenames, then run this script again.
  exit /b 1
)

echo.
echo --- Starting full catalog scan ---
py -m translation_qa scan --config paths.json
exit /b %ERRORLEVEL%
