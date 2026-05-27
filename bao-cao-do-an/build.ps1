# build.ps1 — One-command thesis build
# Usage:
#   .\build.ps1             # full build (requires figures/*.svg)
#   .\build.ps1 -Draft      # draft build (figures shown as placeholders)
#   .\build.ps1 -ConvertOnly  # only re-run convert_all.py, skip typst compile
#
param(
  [string]$LuanVanDir  = "$PSScriptRoot",
  [switch]$Draft,
  [switch]$ConvertOnly
)

$ErrorActionPreference = 'Stop'

# ── Step 1: Convert .md → .typ ───────────────────────────────
Write-Host "`n[1/2] Converting markdown → typst..." -ForegroundColor Cyan
python "$LuanVanDir\scripts\convert_all.py" `
  --root       "$LuanVanDir" `
  --output-dir "$LuanVanDir\typst"

if ($LASTEXITCODE -ne 0) {
  Write-Host "Conversion failed." -ForegroundColor Red
  exit 1
}

if ($ConvertOnly) {
  Write-Host "Done (convert only)." -ForegroundColor Green
  exit 0
}

# ── Step 2: Compile with Typst ────────────────────────────────
Write-Host "`n[2/2] Compiling with Typst..." -ForegroundColor Cyan
New-Item -ItemType Directory -Path "$LuanVanDir\output" -Force | Out-Null

$draftArg = if ($Draft) { @('--input', 'DRAFT=1') } else { @() }

typst compile `
  --root "$LuanVanDir" `
  @draftArg `
  "$LuanVanDir\typst\main.typ" `
  "$LuanVanDir\output\bao-cao-do-an.pdf"

if ($LASTEXITCODE -ne 0) {
  Write-Host "Typst compile failed." -ForegroundColor Red
  exit 1
}

$size = [math]::Round((Get-Item "$LuanVanDir\output\bao-cao-do-an.pdf").Length / 1KB)
Write-Host "`nBuilt: output\bao-cao-do-an.pdf  (${size} KB)" -ForegroundColor Green
