# GraphTriage - one-click setup for Windows 10/11
# Run in PowerShell:  powershell -ExecutionPolicy Bypass -File .\setup-windows.ps1
# Safe to run again at any time.

param([switch]$Update, [switch]$Reset)

$RepoZip    = "https://github.com/Furquan-Shaikh/graphtriage/archive/refs/heads/main.zip"
if ($env:GT_REPO_ZIP) { $RepoZip = $env:GT_REPO_ZIP }
$InstallDir = Join-Path $env:USERPROFILE "graphtriage"
if ($env:GT_INSTALL_DIR) { $InstallDir = $env:GT_INSTALL_DIR }
$Log = Join-Path $env:TEMP "graphtriage-setup.log"
$ProgressPreference = "SilentlyContinue"
try { Start-Transcript -Path $Log -Force | Out-Null } catch {}

function Info($m) { Write-Host "[..] $m" -ForegroundColor Cyan }
function Ok($m)   { Write-Host "[OK] $m" -ForegroundColor Green }
function Warn($m) { Write-Host "[!!] $m" -ForegroundColor Yellow }
function Done($code) { try { Stop-Transcript | Out-Null } catch {}; exit $code }
function Fail($m) {
  Write-Host "[XX] $m" -ForegroundColor Red
  Write-Host "Log file (send this file to whoever shared the project with you if you are stuck): $Log"
  Done 1
}
function Refresh-Path {
  $env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [Environment]::GetEnvironmentVariable("Path","User")
}
function Test-DockerReady {
  try { docker info *> $null; return ($LASTEXITCODE -eq 0) } catch { return $false }
}
function Test-PortFree([int]$p) {
  $c = Get-NetTCPConnection -State Listen -LocalPort $p -ErrorAction SilentlyContinue
  return (-not $c)
}
function Find-FreePort([int]$start) {
  $p = $start
  while (-not (Test-PortFree $p)) { $p++ }
  return $p
}

Write-Host ""
Write-Host "=== GraphTriage setup for Windows ===" -ForegroundColor Cyan
Write-Host ""

# ---------- Step 1: PC check ----------
Info "Step 1/6: Checking your PC"
if (-not [Environment]::Is64BitOperatingSystem) { Fail "64-bit Windows is required." }
$build = [int](Get-CimInstance Win32_OperatingSystem).BuildNumber
if ($build -lt 19044) { Fail "Your Windows is too old (build $build). Update to Windows 10 21H2 or newer, or Windows 11." }
$ramGB = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1)
if ($ramGB -lt 7.5) { Warn "Only $ramGB GB RAM detected. 8 GB or more is recommended; it may run slowly. Close other apps." } else { Ok "RAM: $ramGB GB" }
$drive = $env:SystemDrive.Substring(0,1)
$freeGB = [math]::Round((Get-PSDrive -Name $drive).Free / 1GB, 1)
if ($freeGB -lt 15) { Warn "Only $freeGB GB free on $drive`: . About 15 GB is needed (Docker + images)." } else { Ok "Free disk on $drive`: $freeGB GB" }
$hv = (Get-CimInstance Win32_ComputerSystem).HypervisorPresent
$vt = (Get-CimInstance Win32_Processor | Select-Object -First 1).VirtualizationFirmwareEnabled
if (-not $hv -and -not $vt) { Warn "Virtualization looks disabled in BIOS/UEFI. If Docker fails to start, enable 'Intel VT-x' or 'AMD SVM' in BIOS." } else { Ok "Virtualization OK" }

# ---------- Step 2: Docker ----------
Info "Step 2/6: Checking Docker Desktop"
Refresh-Path
$dockerExe = Join-Path $env:ProgramFiles "Docker\Docker\Docker Desktop.exe"
$haveDocker = [bool](Get-Command docker -ErrorAction SilentlyContinue) -or (Test-Path $dockerExe)
if (-not $haveDocker) {
  $winget = Get-Command winget -ErrorAction SilentlyContinue
  if (-not $winget) {
    Fail "Docker Desktop is not installed and 'winget' is not available. Install Docker Desktop from https://www.docker.com/products/docker-desktop/ , restart the PC, open Docker Desktop once, then run this script again."
  }
  Info "Installing Docker Desktop. A Windows permission prompt will appear - click Yes. This takes a few minutes."
  winget install -e --id Docker.DockerDesktop --accept-package-agreements --accept-source-agreements
  if ($LASTEXITCODE -ne 0) {
    Fail "Docker Desktop install failed. Install it manually from https://www.docker.com/products/docker-desktop/ and run this script again."
  }
  Write-Host ""
  Warn "Docker Desktop is installed. NEXT STEPS:"
  Write-Host "  1) Restart your PC."
  Write-Host "  2) Open 'Docker Desktop' from the Start menu, accept the terms, wait until it says 'Engine running'."
  Write-Host "  3) Run this same script again."
  Done 0
}
if (-not (Test-DockerReady)) {
  if (Test-Path $dockerExe) {
    Info "Starting Docker Desktop..."
    Start-Process $dockerExe
  }
  Info "Waiting for Docker to be ready (up to 5 minutes)..."
  $deadline = (Get-Date).AddMinutes(5)
  while (-not (Test-DockerReady) -and (Get-Date) -lt $deadline) { Start-Sleep -Seconds 10; Write-Host "   still waiting..." }
  if (-not (Test-DockerReady)) {
    Fail "Docker is not running. Open Docker Desktop, accept the terms if it asks, wait until it says 'Engine running', then run this script again."
  }
}
docker compose version *> $null
if ($LASTEXITCODE -ne 0) { Fail "'docker compose' is missing. Update Docker Desktop to the latest version." }
Ok "Docker is ready"

# ---------- Step 3: project files ----------
Info "Step 3/6: Getting the project files"
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }
if ((Test-Path (Join-Path $scriptDir "docker-compose.yml")) -and (Test-Path (Join-Path $scriptDir "db-init"))) {
  $root = $scriptDir
  Ok "Using this folder: $root"
} elseif ((Test-Path (Join-Path $InstallDir "docker-compose.yml")) -and -not $Update) {
  $root = $InstallDir
  Ok "Using existing folder: $root"
} else {
  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
  $zip = Join-Path $env:TEMP "graphtriage.zip"
  $tmp = Join-Path $env:TEMP "graphtriage-extract"
  if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
  try { Invoke-WebRequest -Uri $RepoZip -OutFile $zip -UseBasicParsing } catch { Fail "Could not download the project. Check your internet connection. Details: $($_.Exception.Message)" }
  Expand-Archive -Path $zip -DestinationPath $tmp -Force
  $inner = Get-ChildItem $tmp -Directory | Select-Object -First 1
  $parentDir = Split-Path $InstallDir -Parent
  if ($parentDir -and -not (Test-Path $parentDir)) { New-Item -ItemType Directory -Path $parentDir -Force | Out-Null }
  if (Test-Path $InstallDir) { Copy-Item (Join-Path $inner.FullName "*") $InstallDir -Recurse -Force } else { Move-Item $inner.FullName $InstallDir }
  Remove-Item $zip, $tmp -Recurse -Force -ErrorAction SilentlyContinue
  $root = $InstallDir
  Ok "Project downloaded to: $root"
}
Set-Location $root
if ($Reset) { Warn "Reset requested: removing old containers AND data..."; docker compose down -v }

# ---------- Step 4: already running? ports ----------
Info "Step 4/6: Checking ports"
$running = docker ps --format "{{.Names}}" 2>$null | Select-String "graphtriage-ticketing-service"
$springPort = 8080; $neoHttp = 7474; $neoBolt = 7687
if ($running) {
  Ok "GraphTriage containers are already running"
  if (Test-Path ".env") {
    $envText = Get-Content ".env" -Raw
    if ($envText -match "SPRING_PORT=(\d+)") { $springPort = [int]$Matches[1] }
    if ($envText -match "NEO4J_HTTP_PORT=(\d+)") { $neoHttp = [int]$Matches[1] }
    if ($envText -match "NEO4J_BOLT_PORT=(\d+)") { $neoBolt = [int]$Matches[1] }
  }
} else {
  $wanted = [ordered]@{ SPRING_PORT = 8080; INFERENCE_PORT = 8000; MYSQL_HOST_PORT = 3307; NEO4J_HTTP_PORT = 7474; NEO4J_BOLT_PORT = 7687 }
  $lines = @()
  foreach ($k in $wanted.Keys) {
    $want = $wanted[$k]
    $got = Find-FreePort $want
    if ($got -ne $want) {
      Warn "Port $want is busy, using $got for $k"
      $lines += "$k=$got"
    }
    if ($k -eq "SPRING_PORT") { $springPort = $got }
    if ($k -eq "NEO4J_HTTP_PORT") { $neoHttp = $got }
    if ($k -eq "NEO4J_BOLT_PORT") { $neoBolt = $got }
  }
  $marker = "# generated by setup-windows.ps1"
  if ($lines.Count -gt 0) {
    Set-Content -Path ".env" -Value (@($marker) + $lines) -Encoding ASCII
  } elseif ((Test-Path ".env") -and ((Get-Content ".env" -Raw) -match [regex]::Escape($marker))) {
    Remove-Item ".env" -Force
  }
  Ok "Ports are ready"
}

# ---------- Step 5: start ----------
if ((-not $running) -or $Update) {
  Info "Step 5/6: Starting GraphTriage. First run downloads about 3 GB - please wait (5-15 minutes)..."
  if ($Update) { docker compose up -d --force-recreate } else { docker compose up -d }
  if ($LASTEXITCODE -ne 0) { Fail "'docker compose up' failed. Scroll up to see the error." }
  Info "Loading the knowledge graph (one-time)..."
  $deadline = (Get-Date).AddMinutes(10)
  do {
    Start-Sleep -Seconds 5
    $st = docker inspect -f "{{.State.Status}}|{{.State.ExitCode}}" graphtriage-graph-seed 2>$null
  } while ($st -notlike "exited*" -and (Get-Date) -lt $deadline)
  if ($st -ne "exited|0") {
    docker logs graphtriage-graph-seed 2>&1 | Select-Object -Last 15
    Fail "The graph seed step did not finish correctly (status: $st). If you ran GraphTriage before with different settings, run 'docker compose down -v' in the project folder (this deletes the old data), then run this script again."
  }
  Ok "Knowledge graph loaded"
} else {
  Info "Step 5/6: Skipped (already running)"
}

# ---------- Step 6: wait for the app ----------
Info "Step 6/6: Waiting for the app to answer..."
$base = "http://localhost:$springPort"
$tok = $null
$deadline = (Get-Date).AddMinutes(3)
while (-not $tok -and (Get-Date) -lt $deadline) {
  try {
    $body = @{ username = "demo_user"; password = "ChangeMe123!" } | ConvertTo-Json
    $tok = (Invoke-RestMethod -Method Post -Uri "$base/api/auth/login" -ContentType "application/json" -Body $body).token
  } catch { Start-Sleep -Seconds 5 }
}
if (-not $tok) { Fail "The app did not respond. Run 'docker compose logs ticketing-service' in $root and send the output to whoever shared the project with you." }
Ok "App is up and login works"

Write-Host ""
Write-Host "=== ALL DONE ===" -ForegroundColor Green
Write-Host "App:          $base   (login: demo_user / ChangeMe123!)"
Write-Host "Neo4j graph:  http://localhost:$neoHttp   (login: neo4j / demo_neo4j_pass)"
if ($neoBolt -ne 7687) { Write-Host "              In Neo4j Browser use connect URL: bolt://localhost:$neoBolt" }
Write-Host ""
Write-Host "Project folder: $root"
Write-Host "Stop:           cd `"$root`" ; docker compose down"
Write-Host "Start again:    cd `"$root`" ; docker compose up -d"
Write-Host "Remove all data: cd `"$root`" ; docker compose down -v"
Start-Process $base
Done 0