@echo off
setlocal
cd /d "%~dp0"
if not exist reports mkdir reports

echo Pulling the catalog-scan update (branch cursor/translation-veracity-checker-5bc6)...
git -C "%~dp0..\.." fetch origin cursor/translation-veracity-checker-5bc6
if errorlevel 1 (
  echo git fetch failed. Continuing with the files already on disk.
) else (
  git -C "%~dp0..\.." checkout cursor/translation-veracity-checker-5bc6
  git -C "%~dp0..\.." pull origin cursor/translation-veracity-checker-5bc6
)

copy /Y paths.example.json paths.json >nul

if not exist reports\old-english-interiors mkdir reports\old-english-interiors
echo.
echo --- Archiving leftover English-interior reports from the old scan ---
for %%F in (reports\*DO-NOT-USE*.html reports\*DO-NOT-USE*.csv reports\*DO-NOT-USE*.json reports\*__und.html reports\*__und.csv reports\*__und.json) do (
  if exist "%%F" move /Y "%%F" reports\old-english-interiors\ >nul
)
echo Remaining HTML reports:
dir /b reports\*.html 2>nul
if errorlevel 1 echo   (none - a new catalog scan will start at 0)

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
