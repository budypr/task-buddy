#!/usr/bin/env python3
"""Add or update the Postgres MCP server in ~/.cursor/mcp.json."""

import getpass
import json
import os
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote

try:
    from src.lib import (
        MCP_JSON,
        REPO_ROOT,
        ensure_npx,
        merge_mcp_server,
    )
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src.lib import (
        MCP_JSON,
        REPO_ROOT,
        ensure_npx,
        merge_mcp_server,
    )

CONFIG_JSON = REPO_ROOT / "src" / "store" / "mcp-tools" / "postgres.json"

DEFAULTS = {
    "host": "localhost",
    "port": "5432",
    "user": "postgres",
    "password": "",
    "database": "postgres",
}


def _prompt(label: str, default: str, secret: bool = False) -> str:
    """Prompt for a value; show default in brackets; Enter uses default."""
    if secret:
        if default:
            prompt = f"{label} [****]: "
        else:
            prompt = f"{label} (leave empty if none) []: "
        value = getpass.getpass(prompt)
        return value if value.strip() else default
    prompt = f"{label} [{default}]: "
    value = input(prompt).strip()
    return value if value else default


def build_connection_url(host: str, port: str, user: str, password: str, database: str) -> str:
    """Build a postgresql:// URL with optional percent-encoding for user/password."""
    safe_user = quote(user, safe="") if user else ""
    safe_password = quote(password, safe="") if password else ""
    if safe_password:
        auth = f"{safe_user}:{safe_password}"
    else:
        auth = safe_user if safe_user else ""
    netloc = f"{host}:{port}"
    if auth:
        netloc = f"{auth}@{netloc}"
    return f"postgresql://{netloc}/{quote(database, safe='')}"


def main() -> None:
    if not CONFIG_JSON.exists():
        print(f"error: config not found: {CONFIG_JSON}", file=sys.stderr)
        sys.exit(1)

    if not ensure_npx():
        print("error: npx is required to run the Postgres MCP server but was not found.", file=sys.stderr)
        sys.exit(1)

    url = os.environ.get("POSTGRES_URL")
    if not url:
        print("PostgreSQL connection parameters (press Enter to use default).")
        host = _prompt("Host", DEFAULTS["host"])
        port = _prompt("Port", DEFAULTS["port"])
        user = _prompt("User", DEFAULTS["user"])
        password = _prompt("Password", DEFAULTS["password"], secret=True)
        database = _prompt("Database", DEFAULTS["database"])
        url = build_connection_url(host, port, user, password, database)

    data = json.loads(CONFIG_JSON.read_text())
    if "postgres" not in data or not isinstance(data["postgres"], dict):
        print("error: postgres.json must contain a 'postgres' key with server config", file=sys.stderr)
        sys.exit(1)
    args = data["postgres"].get("args") or []
    data["postgres"]["args"] = [a if a != "REPLACE_WITH_URL" else url for a in args]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f, indent=2)
        tmp_path = Path(f.name)
    try:
        merge_mcp_server(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    print(f"Postgres MCP server added to {MCP_JSON}. Restart Cursor if it is running.")


if __name__ == "__main__":
    main()
