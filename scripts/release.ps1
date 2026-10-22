# GraphTriage - maintainer release script (for the project owner, NOT for end users)
# Publishes new Docker images and updates docker-compose.yml so everyone gets your changes.
#
# Run AFTER you committed your code, on the main branch:
#   powershell -ExecutionPolicy Bypass -File .\scripts\release.ps1 -Services ticketing -DryRun
#   powershell -ExecutionPolicy Bypass -File .\scripts\release.ps1 -Services ticketing
#   powershell -ExecutionPolicy Bypass -File .\scripts\release.ps1 -Services "ticketing,inference"
#   powershell -ExecutionPolicy Bypass -File .\scripts\release.ps1 -Services all
# Services: ticketing (Java + dashboard), inference (Python), graph-seed (graph-etl scripts), all

param(
  [Parameter(Mandatory = $true)]
  [string]$Services,
  [string]$Message = "",
  [switch]$DryRun
)

$Hub = "furquanahmad"
$map = [ordered]@{
  "ticketing"  = @{ Compose = "ticketing-service"; Repo = "graphtriage-ticketing";   Dir = "ticketing-service" }
  "inference"  = @{ Compose = "inference-service"; Repo = "graphtriage-inference";   Dir = "inference-service" }
  "graph-seed" = @{ Compose = "graph-seed";        Repo = "graphtriage-graph-seed";  Dir = "graph-etl" }
}
$utf8 = New-Object System.Text.UTF8Encoding($false)

function Info($m) { Write-Host "[..] $m" -ForegroundColor Cyan }
function Ok($m)   { Write-Host "[OK] $m" -ForegroundColor Green }
function Warn($m) { Write-Host "[!!] $m" -ForegroundColor Yellow }
function Die($m)  { Write-Host "[XX] $m" -ForegroundColor Red; exit 1 }

$root = Split-Path $PSScriptRoot -Parent
Set-Location $root
$composePath = Join-Path $root "docker-compose.yml"
if (-not ((Test-Path $composePath) -and (Test-Path (Join-Path $root "docker-compose.dev.yml")))) {
  Die "docker-compose.yml not found. Run this script from the project (scripts folder inside it)."
}
function Restore-Compose {
  if ($script:original) { [System.IO.File]::WriteAllText($composePath, $script:original, $utf8) }
}

# ---- which services ----
$requested = @($Services -split "[,\s]+" | Where-Object { $_ })
foreach ($r in $requested) {
  if (($r -ne "all") -and (-not $map.Contains($r))) { Die "Unknown service '$r'. Use: ticketing, inference, graph-seed or all." }
}
if ($requested -contains "all") { $targets = @($map.Keys) } else { $targets = @($requested | Select-Object -Unique) }
Info "Services: $($targets -join ', ')"

# ---- git checks ----
$branch = (git branch --show-current)
if ($branch -ne "main") {
  if ($DryRun) { Warn "You are on '$branch'. A real release needs the main branch." }
  else { Die "Switch to the main branch first: git checkout main" }
}
git fetch origin 2>$null
$behindText = git rev-list --count "HEAD..origin/main" 2>$null
if ($behindText -and ([int]$behindText -gt 0)) { Die "Your branch is behind GitHub by $behindText commit(s). Run: git pull" }
$paths = @("docker-compose.yml", "docker-compose.dev.yml", "db-init", "data/generated")
foreach ($t in $targets) { $paths += $map[$t].Dir }
$dirty = @(git status --porcelain -- $paths)
if ($dirty.Count -gt 0) {
  $dirty | ForEach-Object { Write-Host "   $_" }
  Die "Uncommitted changes in the files above. Commit them first: git add <files> ; git commit -m ""your message"""
}
Ok "Git is clean and up to date"

# ---- plan: next tag for every service ----
$compose = [System.IO.File]::ReadAllText($composePath)
$plan = @()
foreach ($t in $targets) {
  $repo = $map[$t].Repo
  $m = [regex]::Match($compose, "image:\s*" + [regex]::Escape("$Hub/$repo") + ":(\d+(?:\.\d+)*)")
  if (-not $m.Success) { Die "Could not find the image line for $repo in docker-compose.yml" }
  $old = $m.Groups[1].Value
  $parts = $old.Split(".")
  $parts[$parts.Length - 1] = [string]([int]$parts[$parts.Length - 1] + 1)
  $new = $parts -join "."
  $code = curl.exe -s -o NUL -w "%{http_code}" "https://hub.docker.com/v2/repositories/$Hub/$repo/tags/$new/"
  if ($code -eq "200") { Die "Tag $new already exists on Docker Hub for $repo. Never reuse a tag; set a newer tag in docker-compose.yml." }
  $plan += [pscustomobject]@{ Service = $t; Compose = $map[$t].Compose; Repo = $repo; Old = $old; New = $new }
}
Write-Host ""
foreach ($p in $plan) { Write-Host ("  {0,-11} {1,-26} {2} -> {3}" -f $p.Service, $p.Repo, $p.Old, $p.New) }
Write-Host ""
if ($DryRun) { Warn "Dry run: nothing was built, pushed or changed."; exit 0 }

# ---- real release ----
docker info *> $null
if ($LASTEXITCODE -ne 0) { Die "Docker Desktop is not running." }
$script:original = [System.IO.File]::ReadAllText($composePath)
$newCompose = $script:original
foreach ($p in $plan) { $newCompose = $newCompose.Replace("$Hub/$($p.Repo):$($p.Old)", "$Hub/$($p.Repo):$($p.New)") }
[System.IO.File]::WriteAllText($composePath, $newCompose, $utf8)

Info "Building images (can take several minutes)..."
$names = @($plan | ForEach-Object { $_.Compose })
docker compose -f docker-compose.yml -f docker-compose.dev.yml build @names
if ($LASTEXITCODE -ne 0) { Restore-Compose; Die "Build failed. docker-compose.yml was restored. Nothing was published." }
Ok "Build finished"

foreach ($p in $plan) {
  $img = "$Hub/$($p.Repo):$($p.New)"
  $pushed = $false
  for ($try = 1; $try -le 4; $try++) {
    Info "Pushing $img (attempt $try/4)"
    docker push $img
    if ($LASTEXITCODE -eq 0) { $pushed = $true; break }
    Start-Sleep -Seconds 20
  }
  if (-not $pushed) { Restore-Compose; Die "Could not push $img. If it says 'denied', run: docker login. docker-compose.yml was restored; nothing was committed." }
  $seen = $false
  for ($i = 1; $i -le 4; $i++) {
    $code = curl.exe -s -o NUL -w "%{http_code}" "https://hub.docker.com/v2/repositories/$Hub/$($p.Repo)/tags/$($p.New)/"
    if ($code -eq "200") { $seen = $true; break }
    Start-Sleep -Seconds 5
  }
  if (-not $seen) { Restore-Compose; Die "Pushed, but Docker Hub does not list tag $($p.New) for $($p.Repo). docker-compose.yml was restored. Check Docker Hub, then run again." }
  Ok "$img is on Docker Hub"
}

if (-not $Message) { $Message = "Release: " + (($plan | ForEach-Object { "$($_.Service) $($_.New)" }) -join ", ") }
git add docker-compose.yml
git commit -m $Message
if ($LASTEXITCODE -ne 0) { Die "git commit failed." }
git push origin main
if ($LASTEXITCODE -ne 0) { Die "git push failed. Images are already on Docker Hub. Fix the problem, then run: git push origin main" }

Write-Host ""
Ok "Released: $(($plan | ForEach-Object { "$($_.Service) $($_.New)" }) -join ', ')"
Write-Host "Next: test like a new user (see MAINTAINER_GUIDE.md), then tell friends to run setup-windows.ps1 with -Update."
Write-Host "To use the new image in your own dev stack: docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d"