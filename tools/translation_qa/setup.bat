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
echo   2. git pull origin cursor/translation-veracity-checker-5bc6
echo   3. py -m translation_qa list --config paths.json
echo      The list must show language codes such as es, de, hi -- not und.
echo      Do not scan English INTERIOR / DO-NOT-USE PDFs. Do not use --llm until list looks right.
echo   4. Then: .\rescan.bat
echo.
exit /b 0
