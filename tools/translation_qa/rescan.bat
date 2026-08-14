@echo off
setlocal
cd /d "%~dp0"
if not exist reports mkdir reports

echo Pulling the catalog-scan update (branch cursor/translation-veracity-checker-5bc6)...
git -C "%~dp0..\.." fetch origin cursor/translation-veracity-checker-5bc6:cursor/translation-veracity-checker-5bc6
if errorlevel 1 (
  echo git fetch failed. If this folder is already up to date, the scan will still run.
) else (
  git -C "%~dp0..\.." checkout cursor/translation-veracity-checker-5bc6
  git -C "%~dp0..\.." pull origin cursor/translation-veracity-checker-5bc6
)

copy /Y paths.example.json paths.json >nul
echo.
echo --- Inventory of every PDF the checker can see ---
py -m translation_qa inventory --config paths.json
echo.
echo --- Books and translation pairs ---
py -m translation_qa list --config paths.json

echo.
echo --- Starting full catalog scan (skips pairs that already have reports) ---
py -m translation_qa scan --config paths.json
echo.
echo Reports: %CD%\reports
echo If the pair count is still too low, paste reports\list.txt and reports\inventory.tsv
echo into the Cursor chat (filenames only; no PDF contents).
echo.
pause
exit /b %ERRORLEVEL%
