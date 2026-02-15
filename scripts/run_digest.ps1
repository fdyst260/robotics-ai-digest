param(
    [Parameter(Mandatory = $true)]
    [string[]]$Rss,
    [string]$DbPath = "data/digest.db",
    [int]$Limit = 10,
    [string]$Source
)

$ErrorActionPreference = "Stop"

$dbDirectory = Split-Path -Path $DbPath -Parent
if ($dbDirectory -and -not (Test-Path $dbDirectory)) {
    New-Item -ItemType Directory -Path $dbDirectory -Force | Out-Null
}

Write-Host "Ingesting feeds into $DbPath ..."
python -m robotics_ai_digest ingest --db $DbPath --rss $Rss
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "Listing recent articles ..."
if ($Source) {
    python -m robotics_ai_digest list --db $DbPath --limit $Limit --source $Source
} else {
    python -m robotics_ai_digest list --db $DbPath --limit $Limit
}
exit $LASTEXITCODE
