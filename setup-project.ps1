# setup-project.ps1
# Medical Promax - Hemato lesson site
# Mode: Validate existing extracted files (NO unzip required)
# Optional: if critical files are missing, can restore from zip.

[CmdletBinding()]
param(
    [switch]$Open,
    [switch]$Clean,
    [switch]$RestoreFromZip,
    [string]$ZipPath = $null
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Info($m) { Write-Host $m -ForegroundColor Cyan }
function Ok($m)   { Write-Host ("[OK] " + $m) -ForegroundColor Green }
function Warn($m) { Write-Host ("[WARN] " + $m) -ForegroundColor Yellow }
function Err($m)  { Write-Host ("[ERROR] " + $m) -ForegroundColor Red }

# Project root = folder containing this script
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

Info ("ProjectRoot: " + $projectRoot)

# --- Optional clean (does NOT delete zip or this script) ---
if ($Clean) {
    Warn "Clean enabled: removing site folders/files (assets/pages/data/tools/index/404/README)"
    $targets = @("assets","pages","data","tools","index.html","404.html","README.md")
    foreach ($t in $targets) {
        $p = Join-Path $projectRoot $t
        if (Test-Path -LiteralPath $p) {
            Remove-Item -LiteralPath $p -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
    Ok "Clean done."
}

# --- Validate existing structure (no unzip) ---
$required = @(
    @{ Name="index.html"; Path=(Join-Path $projectRoot "index.html") },
    @{ Name="assets/styles.css"; Path=(Join-Path $projectRoot "assets\styles.css") },
    @{ Name="assets/app.js"; Path=(Join-Path $projectRoot "assets\app.js") },
    @{ Name="pages folder"; Path=(Join-Path $projectRoot "pages") },
    @{ Name="data folder"; Path=(Join-Path $projectRoot "data") }
)

$missing = @()
foreach ($r in $required) {
    if (-not (Test-Path -LiteralPath $r.Path)) {
        $missing += $r
    }
}

if ($missing.Count -eq 0) {
    Ok "All required files/folders exist. No unzip needed."
} else {
    Warn "Some required items are missing:"
    foreach ($m in $missing) {
        Write-Host (" - " + $m.Name + " :: " + $m.Path) -ForegroundColor Yellow
    }

    if (-not $RestoreFromZip) {
        Warn "RestoreFromZip is OFF. Nothing will be extracted/copied."
        Warn "If you want auto-restore from zip, run:"
        Warn "  .\setup-project.ps1 -RestoreFromZip"
    }
}

# --- Optional restore from zip (only if asked AND missing exists) ---
if ($RestoreFromZip -and $missing.Count -gt 0) {

    # Resolve zip path
    if ([string]::IsNullOrWhiteSpace($ZipPath)) {
        $cand = Get-ChildItem -LiteralPath $projectRoot -Filter "hemato_lesson_site*.zip" -File -ErrorAction SilentlyContinue |
                Sort-Object LastWriteTime -Descending |
                Select-Object -First 1
        if ($null -ne $cand) {
            $ZipPath = $cand.FullName
        }
    } else {
        if (-not [System.IO.Path]::IsPathRooted($ZipPath)) {
            $ZipPath = Join-Path $projectRoot $ZipPath
        }
    }

    if ([string]::IsNullOrWhiteSpace($ZipPath) -or -not (Test-Path -LiteralPath $ZipPath)) {
        Err ("Zip not found. Put hemato_lesson_site.zip in project root or pass -ZipPath")
        exit 1
    }

    Info ("Restoring from zip: " + $ZipPath)

    $temp = Join-Path $env:TEMP ("medicalpromax_restore_" + [Guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $temp -Force | Out-Null

    try {
        Expand-Archive -LiteralPath $ZipPath -DestinationPath $temp -Force

        # If single top folder, use it as source root
        $children = Get-ChildItem -LiteralPath $temp -Force
        $dirs  = $children | Where-Object { $_.PSIsContainer }
        $files = $children | Where-Object { -not $_.PSIsContainer }

        $sourceRoot = $temp
        if ($files.Count -eq 0 -and $dirs.Count -eq 1) {
            $sourceRoot = $dirs[0].FullName
        }

        # Copy everything to project root (overwrite)
        $items = Get-ChildItem -LiteralPath $sourceRoot -Force
        foreach ($it in $items) {
            $dest = Join-Path $projectRoot $it.Name
            Copy-Item -LiteralPath $it.FullName -Destination $dest -Recurse -Force
        }

        Ok "Restore completed."

    } catch {
        Err ("Restore failed: " + $_.Exception.Message)
        exit 1
    } finally {
        if (Test-Path -LiteralPath $temp) {
            Remove-Item -LiteralPath $temp -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

# --- Quick report ---
$pagesDir = Join-Path $projectRoot "pages"
if (Test-Path -LiteralPath $pagesDir) {
    $pageCount = (Get-ChildItem -LiteralPath $pagesDir -Filter "*.html" -File -ErrorAction SilentlyContinue).Count
    Info ("Pages found: " + $pageCount)
}

# --- Open index.html if requested ---
if ($Open) {
    $index = Join-Path $projectRoot "index.html"
    if (Test-Path -LiteralPath $index) {
        Info "Opening index.html..."
        Start-Process $index
        Ok "Opened."
    } else {
        Warn "index.html not found. Cannot open."
    }
}

Ok "Done."
