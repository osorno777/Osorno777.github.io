# Find bookstore translation tools and named workorders only.
# Does not walk church-directory Python under C:\Alertness AI (that was 19k files).
# Does not move or delete anything.
$ErrorActionPreference = "Continue"
$outDir = Join-Path $PSScriptRoot "reports"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$pyOut = Join-Path $outDir "claude_scanners.tsv"
$clueOut = Join-Path $outDir "claude_path_clues.tsv"
$namedOut = Join-Path $outDir "bookstore_clues.tsv"

$roots = @(
    "C:\Alertness AI\bookstore",
    "C:\Alertness AI\website books",
    "C:\Alertness AI\_safety\deploys\econ_translation",
    "C:\Users\dinam\bookstore"
) | Where-Object { Test-Path $_ }

$skipDirs = @(
    "the sims", "the sims 2", "ea games", "node_modules", ".git",
    "__pycache__", "appdata", "cell phone saves", "_safety\backups"
)

function Test-SkipPath([string]$path) {
    $blob = $path.ToLower()
    foreach ($marker in $skipDirs) {
        if ($blob -like "*\$marker\*" -or $blob -like "*\$marker") { return $true }
    }
    return $false
}

Write-Host "Looking for bookstore scanners and named files under:"
$roots | ForEach-Object { Write-Host "  $_" }

$pyRows = New-Object System.Collections.Generic.List[string]
$pyRows.Add("kind`tpath") | Out-Null
$clueRows = New-Object System.Collections.Generic.List[string]
$clueRows.Add("python_file`tline`tclue") | Out-Null

$pyFiles = New-Object System.Collections.Generic.List[string]
foreach ($root in $roots) {
    Get-ChildItem -Path $root -Recurse -File -Filter *.py -ErrorAction SilentlyContinue |
        Where-Object {
            -not (Test-SkipPath $_.FullName) -and
            $_.Name -match '(?i)translat|refusal|epub|lineage|preflight|kdp|fulfill|verif|scan_instruction|bleed|catalog|html'
        } |
        ForEach-Object { $pyFiles.Add($_.FullName) }
}

foreach ($path in ($pyFiles | Select-Object -Unique)) {
    $name = [IO.Path]::GetFileName($path).ToLower()
    $kind = "python"
    if ($name -match 'scan|error|qa|audit|punch|epub|translat|veracity|lint|check|lineage|refusal') {
        $kind = "scanner"
    }
    $pyRows.Add("$kind`t$path") | Out-Null

    $i = 0
    Get-Content -LiteralPath $path -ErrorAction SilentlyContinue |
        ForEach-Object {
            $i++
            $line = $_
            if ($line -match '(?i)password|api[_-]?key|secret|token\s*=') { return }
            if ($line -notmatch '(?i)[A-Za-z]:\\|website books|\.epub|kdp_by_isbn|store_catalog|translations[/\\]private|fulfillment|_out|bookstore|qr_fix') {
                return
            }
            $clip = $line.Trim()
            if ($clip.Length -gt 220) { $clip = $clip.Substring(0, 220) }
            $clueRows.Add("$path`t$i`t$clip") | Out-Null
        }
}

$namedRows = New-Object System.Collections.Generic.List[string]
$namedRows.Add("kind`tpath") | Out-Null
$namedPatterns = @(
    "WORKORDERS_RELAY*.md",
    "WORKORDERS_ALL_LANES*.md",
    "WORKORDERS_PULL_CONTAMINATED*.md",
    "WORKORDERS_AND_STATUS*.md",
    "LAUNCH_TODAY_EN_IT_workorders*.md",
    "CORRECTION_splice_coverage*.md",
    "DEFECT_TAXONOMY*.md",
    "LIC_EN_metadata.md",
    "store_catalog.json",
    "PULL_LIST_*.csv",
    "translate_html.py",
    "fix_refusal_text.py",
    "lineage_detect.py",
    "preflight_book_gate.py",
    "sweep_retail_epub_script_bleed.py",
    "readers_fix_and_deploy.py",
    "verify_fix_landed.py",
    "scan_instruction_leak.py"
)
$namedRoots = @(
    "C:\Alertness AI\bookstore",
    "C:\Alertness AI\_safety\deploys\econ_translation",
    "C:\Users\dinam\bookstore"
) | Where-Object { Test-Path $_ }
foreach ($root in $namedRoots) {
    foreach ($pattern in $namedPatterns) {
        Get-ChildItem -Path $root -Recurse -File -Filter $pattern -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -notmatch '(?i)\\_safety\\backups\\' } |
            ForEach-Object { $namedRows.Add("$pattern`t$($_.FullName)") }
    }
    Get-ChildItem -Path $root -Recurse -Directory -Filter "private" -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName.ToLower() -like "*\admin\translations\private" -and $_.FullName -notmatch '(?i)\\_safety\\backups\\' } |
        ForEach-Object { $namedRows.Add("translations-private`t$($_.FullName)") }
    Get-ChildItem -Path $root -Recurse -Directory -Filter "qr_fix" -ErrorAction SilentlyContinue |
        ForEach-Object { $namedRows.Add("qr-fix`t$($_.FullName)") }
}

$pyRows | Select-Object -Unique | Set-Content -Path $pyOut -Encoding utf8
$clueRows | Select-Object -Unique | Set-Content -Path $clueOut -Encoding utf8
$namedRows | Select-Object -Unique | Set-Content -Path $namedOut -Encoding utf8

Write-Host ""
Write-Host "Python files: $($pyRows.Count - 1)  -> $pyOut"
Write-Host "Path clues:   $($clueRows.Count - 1)  -> $clueOut"
Write-Host "Bookstore named files: $($namedRows.Count - 1)  -> $namedOut"
Write-Host ""
Write-Host "--- scanners ---"
$pyRows | Where-Object { $_ -like "scanner`t*" } | Select-Object -First 40
Write-Host ""
Write-Host "--- bookstore relay / pipeline files ---"
$namedRows | Select-Object -Skip 1 | Select-Object -First 40
Write-Host ""
Write-Host "--- first path clues ---"
$clueRows | Select-Object -Skip 1 | Select-Object -First 40
if ($clueRows.Count -gt 41) { Write-Host "... (see the TSV for the rest)" }
Write-Host ""
Write-Host "Paste reports\bookstore_clues.tsv into the Cursor chat (paths only)."
Write-Host "Do not re-run this against all of C:\Alertness AI. Do not treat sidecar JSON as English."
