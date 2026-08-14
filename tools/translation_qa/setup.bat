@echo off
setlocal
cd /d "%~dp0"

echo Installing translation-qa into this folder:
echo   %CD%
echo.

py -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo pip install failed. Confirm Python is installed: py --version
  exit /b 1
)

if not exist .env copy /Y .env.example .env >nul
if not exist paths.json copy /Y paths.example.json paths.json >nul

echo.
echo Next:
echo   1. Edit .env and set PDF_PASSWORDS=...  (semicolon-separated, no quotes needed)
echo   2. Confirm paths.json points at your English PDFs and C:\Alertness AI\website books
echo   3. Trial run:
echo        py -m translation_qa scan --config paths.json --max-sentences 25
echo.
exit /b 0
