# Find Claude-written Python scanners and extract folder/path clues.
# The book checker skips agent_workflows; those scripts still know where
# EPUBs and store files live. Does not move or delete anything.
$ErrorActionPreference = "Continue"
$outDir = Join-Path $PSScriptRoot "reports"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$pyOut = Join-Path $outDir "claude_scanners.tsv"
$clueOut = Join-Path $outDir "claude_path_clues.tsv"

$roots = @(
    "C:\Alertness AI",
    "C:\Users\dinam\Documents\Writing",
    "C:\Users\dinam\Documents",
    "C:\Users\dinam\.claude",
    "C:\Users\dinam\Claude",
    "C:\Users\dinam\Osorno777.github.io",
    "C:\Users\dinam\bookstore",
    "C:\Alertness AI\bookstore"
) | Where-Object { Test-Path $_ }

$skipDirs = @(
    "the sims", "the sims 2", "ea games", "node_modules", ".git",
    "__pycache__", "appdata", "cell phone saves"
)

function Test-SkipPath([string]$path) {
    $blob = $path.ToLower()
    foreach ($marker in $skipDirs) {
        if ($blob -like "*\$marker\*" -or $blob -like "*\$marker") { return $true }
    }
    return $false
}

Write-Host "Looking for Claude/Python scanners under:"
$roots | ForEach-Object { Write-Host "  $_" }

$pyRows = New-Object System.Collections.Generic.List[string]
$pyRows.Add("kind`tpath") | Out-Null
$clueRows = New-Object System.Collections.Generic.List[string]
$clueRows.Add("python_file`tline`tclue") | Out-Null

$pyFiles = New-Object System.Collections.Generic.List[string]
foreach ($root in $roots) {
    Get-ChildItem -Path $root -Recurse -File -Filter *.py -ErrorAction SilentlyContinue |
        Where-Object { -not (Test-SkipPath $_.FullName) } |
        ForEach-Object { $pyFiles.Add($_.FullName) }
}

foreach ($path in ($pyFiles | Select-Object -Unique)) {
    $name = [IO.Path]::GetFileName($path).ToLower()
    $kind = "python"
    if ($name -match 'scan|error|qa|audit|punch|epub|translat|veracity|lint|check') {
        $kind = "scanner"
    }
    $pyRows.Add("$kind`t$path") | Out-Null

    $i = 0
    Get-Content -LiteralPath $path -ErrorAction SilentlyContinue |
        ForEach-Object {
            $i++
            $line = $_
            if ($line -match '(?i)password|api[_-]?key|secret|token\s*=') { return }
            if ($line -notmatch '(?i)[A-Za-z]:\\|/data/|website books|\.epub|kdp_by_isbn|Alertness|store_epub|agent_workflows|EPUB\\|translations[/\\]private|WORKORDERS_RELAY|LIC_EN_metadata|translate_html|fix_refusal|bookstore') {
                return
            }
            $clip = $line.Trim()
            if ($clip.Length -gt 220) { $clip = $clip.Substring(0, 220) }
            $clueRows.Add("$path`t$i`t$clip") | Out-Null
        }
}

$pyRows | Select-Object -Unique | Set-Content -Path $pyOut -Encoding utf8
$clueRows | Select-Object -Unique | Set-Content -Path $clueOut -Encoding utf8

$namedOut = Join-Path $outDir "bookstore_clues.tsv"
$namedRows = New-Object System.Collections.Generic.List[string]
$namedRows.Add("kind`tpath") | Out-Null
$namedPatterns = @(
    "WORKORDERS_RELAY*.md",
    "LIC_EN_metadata.md",
    "translate_html.py",
    "fix_refusal_text.py"
)
foreach ($root in $roots) {
    foreach ($pattern in $namedPatterns) {
        Get-ChildItem -Path $root -Recurse -File -Filter $pattern -ErrorAction SilentlyContinue |
            Where-Object { -not (Test-SkipPath $_.FullName) } |
            ForEach-Object { $namedRows.Add("$pattern`t$($_.FullName)") }
    }
    Get-ChildItem -Path $root -Recurse -Directory -Filter "private" -ErrorAction SilentlyContinue |
        Where-Object {
            -not (Test-SkipPath $_.FullName) -and
            $_.FullName.ToLower() -like "*\admin\translations\private"
        } |
        ForEach-Object { $namedRows.Add("translations-private`t$($_.FullName)") }
}
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
Write-Host "Paste reports\claude_path_clues.tsv and reports\bookstore_clues.tsv into the Cursor chat"
Write-Host "(paths only, no secrets). Do not treat sidecar JSON text as the original English."
Write-Host "Do not re-run translate_html.py hardening (already landed, task #58)."
