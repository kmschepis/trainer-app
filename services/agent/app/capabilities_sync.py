from __future__ import annotations

import base64
import json
import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List

import httpx
import jwt


def _agent_private_key() -> str:
    key_b64 = os.getenv("AGENT_PRIVATE_KEY_B64", "").strip()
    if key_b64:
        try:
            return base64.b64decode(key_b64.encode("utf-8")).decode("utf-8").strip()
        except Exception as exc:
            raise RuntimeError(f"AGENT_PRIVATE_KEY_B64 invalid: {exc}")

    key = os.getenv("AGENT_PRIVATE_KEY", "").strip()
    if not key:
        raise RuntimeError("AGENT_PRIVATE_KEY(_B64) not configured")
    return key


def _api_base_url() -> str:
    return os.getenv("API_BASE_URL", "http://api:8000").strip().rstrip("/")


def _capabilities_dir() -> Path:
    # Keep generated artifacts inside the agent service so they're easy to audit.
    return Path(__file__).parent / "generated"


def _sign_agent_jwt() -> str:
    now = int(time.time())
    token = jwt.encode(
        {
            "iss": "trainer2-agent",
            "aud": "trainer2-api",
            "iat": now,
            "exp": now + 60,
        },
        _agent_private_key(),
        algorithm="RS256",
    )
    # pyjwt returns str for RS256
    return token


def _atomic_replace_dir(target: Path, source: Path) -> None:
    # `target` is a bind mount in compose (./services/agent/app/generated -> /app/app/generated).
    # Deleting the mountpoint directory itself fails with "Device or resource busy".
    # Instead, clear its contents and then move/copy the new contents in.
    target.mkdir(parents=True, exist_ok=True)

    for child in list(target.iterdir()):
        try:
            if child.is_dir() and not child.is_symlink():
                shutil.rmtree(child)
            else:
                child.unlink()
        except FileNotFoundError:
            continue

    for child in list(source.iterdir()):
        dest = target / child.name
        try:
            child.replace(dest)
        except OSError:
            # Cross-device rename or other filesystem edge cases.
            if child.is_dir() and not child.is_symlink():
                shutil.copytree(child, dest, dirs_exist_ok=True)
                shutil.rmtree(child)
            else:
                shutil.copy2(child, dest)
                child.unlink()


def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


async def update_capabilities() -> Dict[str, Any]:
    """Fetch /capabilities from the API and materialize it into auditable files.

    Output layout:
      generated/
        index.json
        tools/<name>.json
        table_cards/<id>.md
        raw/capabilities.json
    """

    api = _api_base_url()
    token = _sign_agent_jwt()

    async with httpx.AsyncClient(timeout=10.0) as http:
        resp = await http.get(
            f"{api}/capabilities",
            headers={"Authorization": f"Bearer {token}"},
        )
        resp.raise_for_status()
        caps: Dict[str, Any] = resp.json()

    tmp_root = Path(tempfile.mkdtemp(prefix="trainer2-capabilities-"))
    try:
        out_root = tmp_root / "generated"
        tools_dir = out_root / "tools"
        cards_dir = out_root / "table_cards"
        raw_dir = out_root / "raw"
        tools_dir.mkdir(parents=True, exist_ok=True)
        cards_dir.mkdir(parents=True, exist_ok=True)
        raw_dir.mkdir(parents=True, exist_ok=True)

        _write_json(raw_dir / "capabilities.json", caps)

        tools: List[Dict[str, Any]] = caps.get("tools") if isinstance(caps.get("tools"), list) else []
        table_cards: List[Dict[str, Any]] = (
            caps.get("tableCards") if isinstance(caps.get("tableCards"), list) else []
        )

        tool_names: List[str] = []
        for t in tools:
            if not isinstance(t, dict):
                continue
            fn = t.get("function") if isinstance(t.get("function"), dict) else None
            name = fn.get("name") if isinstance(fn, dict) else None
            if not isinstance(name, str) or not name.strip():
                continue
            tool_names.append(name)
            _write_json(tools_dir / f"{name}.json", t)

        card_ids: List[str] = []
        for c in table_cards:
            if not isinstance(c, dict):
                continue
            cid = c.get("id")
            md = c.get("markdown")
            if not isinstance(cid, str) or not cid.strip():
                continue
            if not isinstance(md, str):
                md = ""
            card_ids.append(cid)
            _write_text(cards_dir / f"{cid}.md", md)

        index = {
            "version": caps.get("version"),
            "generatedAt": caps.get("generatedAt"),
            "sha256": caps.get("sha256"),
            "tools": sorted(tool_names),
            "tableCards": sorted(card_ids),
        }
        _write_json(out_root / "index.json", index)

        # Swap into place atomically-ish (replace directory).
        target = _capabilities_dir()
        _atomic_replace_dir(target, out_root)
    finally:
        if tmp_root.exists():
            shutil.rmtree(tmp_root, ignore_errors=True)

    return {"ok": True, "sha256": caps.get("sha256")}


def load_tools_from_generated() -> List[Dict[str, Any]]:
    tools_dir = _capabilities_dir() / "tools"
    if not tools_dir.exists():
        return []

    tools: List[Dict[str, Any]] = []
    for path in sorted(tools_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                tools.append(data)
        except Exception:
            continue
    return tools
