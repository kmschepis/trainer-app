$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Resolve-Path (Join-Path $ScriptDir '..\..')
Set-Location $RootDir

$ProjectName = if ($env:COMPOSE_PROJECT_NAME) { $env:COMPOSE_PROJECT_NAME } else { Split-Path -Leaf $RootDir }
$DbVolume = "${ProjectName}_db_data"

if ($args.Count -eq 0 -or $args[0] -ne '--yes') {
  Write-Host "WARNING: This will DELETE the Postgres data volume: $DbVolume"
  Write-Host "All database data will be lost." 
  $confirm = Read-Host "Type 'reset' to continue"
  if ($confirm -ne 'reset') {
    Write-Host 'Aborted.'
    exit 1
  }
}

Write-Host 'Stopping db container (if running)...'
try { docker compose -f compose.yml stop db | Out-Null } catch {}

Write-Host 'Removing db container (if present)...'
try { docker compose -f compose.yml rm -f db | Out-Null } catch {}

Write-Host "Removing volume $DbVolume (if present)..."
try { docker volume rm -f $DbVolume | Out-Null } catch {}

Write-Host 'Starting db...'
docker compose -f compose.yml up -d db | Out-Null

Write-Host 'Waiting for Postgres to accept connections...'
$pgUser = if ($env:POSTGRES_USER) { $env:POSTGRES_USER } else { 'trainer' }
for ($i = 0; $i -lt 30; $i++) {
  try {
    docker compose -f compose.yml exec -T db pg_isready -U $pgUser | Out-Null
    break
  } catch {
    Start-Sleep -Seconds 1
    if ($i -eq 29) {
      throw 'Postgres did not become ready in time.'
    }
  }
}

Write-Host 'Running Alembic migrations...'
docker compose -f compose.yml run --rm api alembic upgrade head

Write-Host 'Done. DB reset and migrated.'
