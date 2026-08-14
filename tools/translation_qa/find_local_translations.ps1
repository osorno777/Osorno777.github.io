# Search this Windows PC for Alertness Books translations the checker has not
# been seeing (store-slug EPUBs and PDFs). Prints a TSV to reports\local_find.tsv.
# Does not move or delete anything.
$ErrorActionPreference = "Continue"
$outDir = Join-Path $PSScriptRoot "reports"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$out = Join-Path $outDir "local_find.tsv"

$roots = @(
    "C:\Alertness AI",
    "C:\Users\dinam\Documents\Writing"
) | Where-Object { Test-Path $_ }

$slugPattern = '^(econ-aifinance|econ-phd|econ-austrian|econ-publicchoice|econ-nie|econ-survivingcj|btc-[1-5]|btw|su_|su-|novel_|vintage_bg|vintage_ctpp|vintage_primer|vintage_pp|vintage_breg|vintage_bldreg|vintage_prolife|vintage_linc)'

Write-Host "Searching for .epub and store-slug files under:"
$roots | ForEach-Object { Write-Host "  $_" }

$rows = New-Object System.Collections.Generic.List[string]
$rows.Add("kind`tpath") | Out-Null

foreach ($root in $roots) {
    Get-ChildItem -Path $root -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object {
            $ext = $_.Extension.ToLower()
            $ext -in @(".epub", ".pdf", ".txt") -and (
                $ext -eq ".epub" -or $_.Name -match $slugPattern
            )
        } |
        ForEach-Object {
            $kind = if ($_.Extension.ToLower() -eq ".epub") { "epub" } else { "slug" }
            $rows.Add("$kind`t$($_.FullName)")
        }
}

$unique = $rows | Select-Object -Unique
$unique | Set-Content -Path $out -Encoding utf8
Write-Host ""
Write-Host "Wrote $out"
Write-Host ("Unique rows: {0}" -f ($unique.Count - 1))
$unique | Select-Object -First 50
if ($unique.Count -gt 51) { Write-Host "... (see the TSV for the rest)" }
Write-Host ""
Write-Host "If this list is still small, copy the store EPUBs off the server (see README)."
