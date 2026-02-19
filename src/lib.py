from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# Repo root: parent of src/
REPO_ROOT = Path(__file__).resolve().parent.parent
CURSOR_DIR = Path.home() / ".cursor"
MCP_JSON = CURSOR_DIR / "mcp.json"
SKILLS_SRC_DIR = REPO_ROOT / "src" / "store" / "skills"
CURSOR_SKILLS_DIR = Path.home() / ".cursor" / "skills"
REPO_REASONING_APPROACH = SKILLS_SRC_DIR / "REASONING_APPROACH.md"
CURSOR_RULES_DIR = Path.home() / ".cursor" / "rules"
REPO_CRITICAL_REASONING_RULE = REPO_ROOT / ".cursor" / "rules" / "critical-reasoning.mdc"

REASONING_REFERENCE_BLOCK = """
## Reasoning approach

When applying this skill, read and follow the instructions in `~/.cursor/skills/REASONING_APPROACH.md` (skills root).
"""


# --- MCP ---

def ensure_npx() -> bool:
    """Ensure npx is available; try to install Node.js (macOS/Homebrew) if missing."""
    if shutil.which("npx"):
        return True
    print("npx not found. Attempting to install Node.js...")
    if platform.system() == "Darwin" and shutil.which("brew"):
        print("Running: brew install node")
        if subprocess.run(["brew", "install", "node"], check=False).returncode == 0:
            if shutil.which("npx"):
                print("Node.js and npx installed successfully.")
                return True
    print("Could not install Node.js automatically.", file=sys.stderr)
    print("Install manually:", file=sys.stderr)
    print("  - macOS (Homebrew): brew install node", file=sys.stderr)
    print("  - Or download from https://nodejs.org", file=sys.stderr)
    return False


def ensure_mcp_json() -> None:
    """Ensure ~/.cursor exists and mcp.json has mcpServers object."""
    CURSOR_DIR.mkdir(parents=True, exist_ok=True)
    if not MCP_JSON.exists():
        MCP_JSON.write_text('{"mcpServers":{}}')
        return
    try:
        data = json.loads(MCP_JSON.read_text())
        if isinstance(data.get("mcpServers"), dict):
            return
    except (json.JSONDecodeError, TypeError):
        pass
    backup = MCP_JSON.with_suffix(f".bak.{os.getpid()}.json")
    if MCP_JSON.exists():
        shutil.copy(MCP_JSON, backup)
    MCP_JSON.write_text('{"mcpServers":{}}')


def merge_mcp_server(snippet_path: Path) -> None:
    """Merge snippet JSON (object with server keys) into mcp.json .mcpServers."""
    ensure_mcp_json()
    if not snippet_path.exists():
        raise FileNotFoundError(f"Config not found: {snippet_path}")
    snippet = json.loads(snippet_path.read_text())
    if not isinstance(snippet, dict):
        raise ValueError("Snippet must be a JSON object")
    data = json.loads(MCP_JSON.read_text())
    servers = data.get("mcpServers") or {}
    if not isinstance(servers, dict):
        servers = {}
    servers.update(snippet)
    data["mcpServers"] = servers
    MCP_JSON.write_text(json.dumps(data, indent=2))


# --- Skills (src/store/skills/*.md -> ~/.cursor/skills/<stem>/SKILL.md) ---

def _frontmatter_value(path: Path, key: str) -> str | None:
    with open(path) as f:
        in_fm = False
        for line in f:
            line = line.rstrip()
            if line.strip() == "---":
                if in_fm:
                    break
                in_fm = True
                continue
            if in_fm and line.startswith(f"{key}:"):
                return line[len(key) + 1 :].strip()
    return None


def discover_skills() -> list[tuple[str, str, str, str]]:
    """Return list of (stem, name, description, mcp) for each .md in src/store/skills/."""
    if not SKILLS_SRC_DIR.is_dir():
        return []
    out = []
    for f in sorted(SKILLS_SRC_DIR.glob("*.md")):
        stem = f.stem
        if stem == "REASONING_APPROACH":
            continue
        name = _frontmatter_value(f, "name") or stem
        desc = _frontmatter_value(f, "description") or "(no description)"
        mcp = _frontmatter_value(f, "mcp") or ""
        out.append((stem, name, desc, mcp))
    return out


def skill_installed(stem: str) -> bool:
    """Return True if the skill is already installed at ~/.cursor/skills/<stem>/."""
    return (CURSOR_SKILLS_DIR / stem).exists()


def _ensure_reasoning_approach_at_skills_root() -> None:
    """Copy repo's REASONING_APPROACH.md to the skills root if present (overwrites by default)."""
    if not REPO_REASONING_APPROACH.is_file():
        return
    CURSOR_SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPO_REASONING_APPROACH, CURSOR_SKILLS_DIR / "REASONING_APPROACH.md")


def _inject_reasoning_reference(skill_content: str) -> str:
    """Insert the reasoning reference block after the first top-level heading (# )."""
    lines = skill_content.splitlines(keepends=True)
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("# ") and not stripped.startswith("## "):
            insert = REASONING_REFERENCE_BLOCK.strip() + "\n\n"
            return "".join(lines[: i + 1]) + insert + "".join(lines[i + 1 :])
    return skill_content


def install_critical_reasoning_rule() -> bool:
    """Copy repo's critical-reasoning.mdc to ~/.cursor/rules/ (user-level). Returns True if installed."""
    if not REPO_CRITICAL_REASONING_RULE.is_file():
        return False
    CURSOR_RULES_DIR.mkdir(parents=True, exist_ok=True)
    dest = CURSOR_RULES_DIR / "critical-reasoning.mdc"
    shutil.copy2(REPO_CRITICAL_REASONING_RULE, dest)
    print(f"Installed user-level rule: {dest}")
    return True


def install_skill(stem: str) -> None:
    """Copy src/store/skills/<stem>.md -> ~/.cursor/skills/<stem>/SKILL.md.
    Copies REASONING_APPROACH.md from repo to the skills root (overwrites if present),
    and injects a reference (not the full content) after the first heading.
    """
    src = SKILLS_SRC_DIR / f"{stem}.md"
    if not src.is_file():
        raise FileNotFoundError(f"Invalid skill: {stem}")
    _ensure_reasoning_approach_at_skills_root()
    dest_dir = CURSOR_SKILLS_DIR / stem
    CURSOR_SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True)
    content = src.read_text()
    fragment_at_root = CURSOR_SKILLS_DIR / "REASONING_APPROACH.md"
    if fragment_at_root.is_file():
        content = _inject_reasoning_reference(content)
    dest_dir.joinpath("SKILL.md").write_text(content)
    print(f"Installed: {stem} -> {dest_dir / 'SKILL.md'}")
