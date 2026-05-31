#Stop on error
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host ""
Write-Host "  CBS Bot (Personal)" -ForegroundColor Cyan
Write-Host "  ==================" -ForegroundColor Cyan
Write-Host ""

# ครั้งแรก — ยังไม่มี .env
if (-not (Test-Path ".env")) {
    Write-Host "  ยังไม่มี .env — เริ่ม setup..." -ForegroundColor Yellow
    python setup.py
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Host ""
}

# ติดตั้ง/อัปเดต packages เงียบๆ
python -m pip install -r requirements.txt -q 2>$null

Write-Host "  กำลังเริ่ม bot..." -ForegroundColor Green
Write-Host "  กด Ctrl+C เพื่อหยุด" -ForegroundColor DarkGray
Write-Host ""

python main.py
