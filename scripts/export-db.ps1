# GraphTriage - maintainer script (not for end users)
# Exports the current MySQL data into db-init/01-init.sql.
# The app_user table is exported WITHOUT data (the app creates the demo user on start).
# Run from anywhere while your local stack is running (container graphtriage-mysql):
#   powershell -ExecutionPolicy Bypass -File .\scripts\export-db.ps1
# Then: review "git diff --stat db-init", commit and push.
# Friends update with: setup-windows.ps1 -Update -Reset

$root = Split-Path $PSScriptRoot -Parent
Set-Location $root

docker info *> $null
if ($LASTEXITCODE -ne 0) { throw "Docker Desktop is not running." }
if (-not (docker ps --format "{{.Names}}" | Select-String -SimpleMatch "graphtriage-mysql")) {
  throw "Container graphtriage-mysql is not running. Start your local stack first."
}

$sh = Join-Path $PSScriptRoot "export-db.sh"
docker cp $sh graphtriage-mysql:/tmp/export-db.sh
docker exec graphtriage-mysql sh /tmp/export-db.sh
New-Item -ItemType Directory -Force (Join-Path $root "db-init") | Out-Null
$sql = Join-Path $root "db-init\01-init.sql"
docker cp graphtriage-mysql:/tmp/init.sql $sql
docker exec graphtriage-mysql rm -f /tmp/init.sql /tmp/export-db.sh

if (-not (Test-Path $sql) -or (Get-Item $sql).Length -lt 1000) { throw "Export failed (file missing or too small)." }
$leak = @(Select-String -Path $sql -Pattern 'INSERT INTO `app_user`').Count
if ($leak -gt 0) { throw "app_user data found in the dump. Do NOT commit this file." }

Write-Host ""
Write-Host "[OK] Exported to db-init\01-init.sql ({0:N0} KB)" -f ((Get-Item $sql).Length / 1KB) -ForegroundColor Green
Write-Host "INSERT lines per table:"
Select-String -Path $sql -Pattern "^INSERT INTO" | ForEach-Object { ($_.Line -split ' ')[2] } | Group-Object | Select-Object Name, Count | Format-Table -AutoSize
Write-Host "Next: git diff --stat db-init ; git add db-init ; git commit -m ""Update data"" ; git push origin main"
Write-Host "Friends then run setup-windows.ps1 with: -Update -Reset"