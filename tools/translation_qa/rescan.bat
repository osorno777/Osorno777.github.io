@echo off
setlocal
cd /d "%~dp0"
if not exist reports mkdir reports

set "QA_ROOT=E:\translation_qa"
set "QA_REPORTS=%QA_ROOT%\reports"
set "QA_TMP=%QA_ROOT%\tmp"
set "QA_PYC=%QA_ROOT%\pycache"

echo === Moving reports and temp files from C: onto E: (before git pull) ===
if not exist E:\ (
  echo Drive E: is not ready. Assign letter E: to the extra disk and run this again.
  pause
  exit /b 1
)
mkdir "%QA_REPORTS%" 2>nul
mkdir "%QA_TMP%" 2>nul
mkdir "%QA_PYC%" 2>nul
mkdir "%QA_ROOT%\pip-cache" 2>nul

set "TMP=%QA_TMP%"
set "TEMP=%QA_TMP%"
set "TMPDIR=%QA_TMP%"
set "TEMPDIR=%QA_TMP%"
set "PYTHONPYCACHEPREFIX=%QA_PYC%"
set "PYTHONUNBUFFERED=1"
set "PIP_CACHE_DIR=%QA_ROOT%\pip-cache"

if exist "%~dp0reports\*.json" del /q "%~dp0reports\*.json" 2>nul
if exist "%~dp0reports\*.csv" del /q "%~dp0reports\*.csv" 2>nul
if exist "%~dp0reports\" (
  echo Moving C:\ reports to %QA_REPORTS%
  robocopy "%~dp0reports" "%QA_REPORTS%" /E /MOVE /R:1 /W:1 /NFL /NDL /NJH /NJS
  if errorlevel 8 (
    echo Could not move reports onto E:.
    pause
    exit /b 1
  )
)
if exist "%~dp0translation_qa\__pycache__\" robocopy "%~dp0translation_qa\__pycache__" "%QA_PYC%\translation_qa_pycache" /E /MOVE /R:1 /W:1 /NFL /NDL /NJH /NJS >nul
if exist "%~dp0tests\__pycache__\" robocopy "%~dp0tests\__pycache__" "%QA_PYC%\tests_pycache" /E /MOVE /R:1 /W:1 /NFL /NDL /NJH /NJS >nul
if exist "%~dp0.pytest_cache\" robocopy "%~dp0.pytest_cache" "%QA_PYC%\pytest_cache" /E /MOVE /R:1 /W:1 /NFL /NDL /NJH /NJS >nul
mkdir "%~dp0reports" 2>nul

echo.
echo Pulling the catalog-scan update (branch cursor/translation-veracity-checker-5bc6)...
git -C "%~dp0..\.." fetch origin cursor/translation-veracity-checker-5bc6
if errorlevel 1 (
  echo git fetch failed. Continuing with the files already on disk.
) else (
  git -C "%~dp0..\.." checkout cursor/translation-veracity-checker-5bc6
  git -C "%~dp0..\.." pull origin cursor/translation-veracity-checker-5bc6
)

py -m translation_qa use-drive --letter E --repo "%~dp0."
if errorlevel 1 (
  copy /Y paths.example.json paths.json >nul
  py -c "import json; from pathlib import Path; p=Path('paths.json'); d=json.loads(p.read_text(encoding='utf-8')); d['output_dir']=r'E:\\translation_qa\\reports'; p.write_text(json.dumps(d, indent=2)+chr(10), encoding='utf-8')"
)

if not exist "%QA_REPORTS%\old-english-interiors" mkdir "%QA_REPORTS%\old-english-interiors"
echo.
echo --- Archiving leftover reports from the old wrong-book scan ---
for %%F in (%QA_REPORTS%\*DO-NOT-USE*.html %QA_REPORTS%\*DO-NOT-USE*.csv %QA_REPORTS%\*DO-NOT-USE*.json %QA_REPORTS%\*INTERIOR*.html %QA_REPORTS%\*INTERIOR*.csv %QA_REPORTS%\*INTERIOR*.json %QA_REPORTS%\*__und.html %QA_REPORTS%\*__und.csv %QA_REPORTS%\*__und.json %QA_REPORTS%\christian-theology-of-public-policy__Public_Choice*.* %QA_REPORTS%\primer-on-modern-themes__Austrian*.* %QA_REPORTS%\life-in-chile__*surviving*.* %QA_REPORTS%\hong*icons*.*) do (
  if exist "%%F" move /Y "%%F" "%QA_REPORTS%\old-english-interiors\" >nul
)
echo Remaining HTML reports on E::
dir /b "%QA_REPORTS%\*.html" 2>nul
if errorlevel 1 echo   (none - a new catalog scan will start at 0)

echo.
echo --- Freeing disk: delete bulky JSON/CSV copies and shrink oversized HTML (summaries kept) ---
py -m translation_qa compact-reports --output "%QA_REPORTS%"

echo.
echo --- Inventory of every PDF the checker can see ---
py -m translation_qa inventory --config paths.json
echo.
echo --- Books and translation pairs ---
py -m translation_qa list --config paths.json

echo.
echo --- Starting full catalog scan (skips pairs that already have reports) ---
echo Reports and temp: %QA_REPORTS%
py -m translation_qa scan --config paths.json
echo.
echo Reports: %QA_REPORTS%
echo If the pair count is still too low, paste E:\translation_qa\reports\list.txt
echo and E:\translation_qa\reports\inventory.tsv into the Cursor chat (filenames only).
echo.
pause
exit /b %ERRORLEVEL%
