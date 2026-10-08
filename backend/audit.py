from datetime import datetime, timezone
import json
from pathlib import Path

AUDIT_PATH = Path(__file__).resolve().parents[1] / "output" / "audit_trail.json"

def audit_event(tool_name: str, args=None, result=None, stop_reason: str | None = None):
    """Append one redacted, bounded JSON record; never include passwords or API keys."""
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    safe_args = {str(k): str(v)[:240] for k, v in (args or {}).items() if k not in {"password", "password_hash", "api_key"}}
    record = {"time": datetime.now(timezone.utc).isoformat(), "tool_name": tool_name, "args": safe_args, "result": str(result)[:500] if result is not None else None, "stop_reason": stop_reason}
    with AUDIT_PATH.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, ensure_ascii=True) + "\n")
