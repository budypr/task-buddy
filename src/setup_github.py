#!/usr/bin/env python3
"""Add or update the GitHub MCP server in ~/.cursor/mcp.json."""

import os
import sys
from pathlib import Path

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

CONFIG_JSON = REPO_ROOT / "src" / "store" / "mcp-tools" / "github.json"


def main() -> None:
    if not CONFIG_JSON.exists():
        print(f"error: config not found: {CONFIG_JSON}", file=sys.stderr)
        sys.exit(1)

    if not ensure_npx():
        print("error: npx is required to run the GitHub MCP server but was not found.", file=sys.stderr)
        sys.exit(1)

    token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not token:
        print("GITHUB_PERSONAL_ACCESS_TOKEN is not set.")
        try:
            import getpass

            token = getpass.getpass("Paste your GitHub Personal Access Token (will not be echoed): ")
        except (ImportError, KeyboardInterrupt):
            token = ""
        if not token:
            print("error: token is required", file=sys.stderr)
            sys.exit(1)

    import json

    data = json.loads(CONFIG_JSON.read_text())
    if "github" not in data or not isinstance(data["github"], dict):
        print("error: github.json must contain a 'github' key with server config", file=sys.stderr)
        sys.exit(1)
    data["github"].setdefault("env", {})["GITHUB_PERSONAL_ACCESS_TOKEN"] = token

    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f, indent=2)
        tmp_path = Path(f.name)
    try:
        merge_mcp_server(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    print(f"GitHub MCP server added to {MCP_JSON}. Restart Cursor if it is running.")


if __name__ == "__main__":
    main()
