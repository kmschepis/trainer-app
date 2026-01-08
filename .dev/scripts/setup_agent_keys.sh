#!/usr/bin/env bash
set -euo pipefail

# Generates an RSA keypair for agent↔api auth and writes base64 values into .env.
# Works well on Windows via Git Bash because .env cannot safely hold multiline PEM.

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
secrets_dir="$root_dir/.dev/secrets/agent"
mkdir -p "$secrets_dir"

priv_pem="$secrets_dir/agent_private.pem"
pub_pem="$secrets_dir/agent_public.pem"

if [[ ! -f "$priv_pem" || ! -f "$pub_pem" ]]; then
  echo "Generating agent RSA keypair in $secrets_dir"
  openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out "$priv_pem" >/dev/null 2>&1
  openssl rsa -pubout -in "$priv_pem" -out "$pub_pem" >/dev/null 2>&1
fi

# Portable base64 one-liner (no wraps)
b64() {
  if command -v base64 >/dev/null 2>&1; then
    base64 -w 0
  else
    python - <<'PY'
import base64,sys
sys.stdout.write(base64.b64encode(sys.stdin.buffer.read()).decode('utf-8'))
PY
  fi
}

priv_b64="$(cat "$priv_pem" | b64)"
pub_b64="$(cat "$pub_pem" | b64)"

env_file="$root_dir/.env"

upsert_env() {
  local key="$1"
  local value="$2"
  if grep -qE "^${key}=" "$env_file"; then
    # macOS sed differs; use python for portability
    python - <<PY
import io
import re
from pathlib import Path
p=Path(r"$env_file")
text=p.read_text(encoding='utf-8').splitlines(True)
out=[]
found=False
for line in text:
    if re.match(r'^'+re.escape("$key")+r'=', line):
        out.append("$key=\"" + "$value" + "\"\n")
        found=True
    else:
        out.append(line)
if not found:
    out.append("$key=\"" + "$value" + "\"\n")
p.write_text(''.join(out), encoding='utf-8')
PY
  else
    printf '\n%s="%s"\n' "$key" "$value" >> "$env_file"
  fi
}

upsert_env "AGENT_PRIVATE_KEY_B64" "$priv_b64"
upsert_env "AGENT_PUBLIC_KEY_B64" "$pub_b64"

echo "Wrote AGENT_PRIVATE_KEY_B64 and AGENT_PUBLIC_KEY_B64 into $env_file"
echo "Next: docker compose up -d --build api agent && curl -X POST http://localhost:9000/update"