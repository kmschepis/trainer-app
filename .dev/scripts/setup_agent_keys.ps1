param(
  [switch]$Force
)

# Generates an RSA keypair for agent↔api auth and writes base64 values into .env.
# This avoids multiline PEM values (which are painful in Windows env / .env files).

$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$SecretsDir = Join-Path $Root ".dev\secrets\agent"
New-Item -ItemType Directory -Force -Path $SecretsDir | Out-Null

$PrivPem = Join-Path $SecretsDir "agent_private.pem"
$PubPem  = Join-Path $SecretsDir "agent_public.pem"

if ($Force -or !(Test-Path $PrivPem) -or !(Test-Path $PubPem)) {
  if (!(Get-Command openssl -ErrorAction SilentlyContinue)) {
    throw "openssl not found in PATH. Use Git Bash to run .dev/scripts/setup_agent_keys.sh, or install OpenSSL."
  }

  Write-Host "Generating agent RSA keypair in $SecretsDir"
  & openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out $PrivPem | Out-Null
  & openssl rsa -pubout -in $PrivPem -out $PubPem | Out-Null
}

$PrivB64 = [Convert]::ToBase64String([System.IO.File]::ReadAllBytes($PrivPem))
$PubB64  = [Convert]::ToBase64String([System.IO.File]::ReadAllBytes($PubPem))

$EnvFile = Join-Path $Root ".env"
if (!(Test-Path $EnvFile)) { New-Item -ItemType File -Path $EnvFile | Out-Null }

function Upsert-EnvLine([string]$Key, [string]$Value) {
  $lines = Get-Content $EnvFile -Raw
  $pattern = "(?m)^" + [Regex]::Escape($Key) + "=.*$"
  $replacement = "$Key=\"$Value\""

  if ([Regex]::IsMatch($lines, $pattern)) {
    $lines = [Regex]::Replace($lines, $pattern, $replacement)
  } else {
    if (-not $lines.EndsWith("`n")) { $lines += "`n" }
    $lines += "$replacement`n"
  }

  Set-Content -Path $EnvFile -Value $lines -Encoding UTF8
}

Upsert-EnvLine "AGENT_PRIVATE_KEY_B64" $PrivB64
Upsert-EnvLine "AGENT_PUBLIC_KEY_B64" $PubB64

Write-Host "Wrote AGENT_PRIVATE_KEY_B64 and AGENT_PUBLIC_KEY_B64 into $EnvFile"
Write-Host "Next: docker compose up -d --build api agent; then: curl -X POST http://localhost:9000/update"