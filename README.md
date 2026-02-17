# Task-buddy

Setup scripts for MCP tools and Cursor skills at user level (`~/.cursor/`).

## Prerequisites

- **Python 3.8+**
- **Node.js / npx** – required for the GitHub and Postgres MCP servers; the setup script can install it via Homebrew on macOS, or install from [nodejs.org](https://nodejs.org)

## MCP tools

User-level config: `~/.cursor/mcp.json`. Scripts merge new servers into existing config.

### GitHub

Requires **Node.js/npx** (the MCP server runs via `npx`). If npx is missing, the script will try to install Node.js (on macOS with Homebrew).

```bash
export GITHUB_PERSONAL_ACCESS_TOKEN='your_github_pat'
python3 src/setup_github.py
# or after: pip install -e .
task-buddy-github
```

Create a [GitHub Personal Access Token](https://github.com/settings/tokens) with repo and (as needed) issues/PRs scope.

### Postgres

Connect to PostgreSQL for read-only queries and schema discovery. Requires **Node.js/npx** (same as GitHub).

```bash
python3 src/setup_postgres.py
# or after: pip install -e .
task-buddy-postgres
```

The script prompts for host, port, user, password, and database. Defaults are shown in brackets (e.g. host=localhost, port=5432, user=postgres, database=postgres); press Enter to accept each default. To skip prompts, set `POSTGRES_URL` to a full connection string. Restart Cursor after setup.

## Skills

Install Cursor skills into `~/.cursor/skills/`:

```bash
python3 src/setup_skills.py
# or after: pip install -e .
task-buddy-skills
```

You’ll see a table of available skills. Enter a **number** to install one, **multiple numbers** (e.g. `1 3 5`) for several, or **all** to install every skill.

**Bundled skills**

| Skill | Description |
|-------|-------------|
| **pg-ask** | Answer Postgres questions and write SQL using the Postgres MCP (schema discovery, parameterized queries). |
| **squash-this** | Structured workflow ASK → PLAN → TECHNICAL DETAILS → IMPLEMENT; requires a GitHub issue. |
| **new-issue** | Create GitHub issues with type labels (bug, feature, spike). |

## Project layout

- **src/** – Python package; `lib.py` holds shared MCP and skills helpers; `setup_github.py` / `setup_postgres.py` / `setup_skills.py` are the entry points.
- **src/store/mcp-tools/** – MCP config snippets (e.g. `github.json`, `postgres.json`). Scripts merge these into `~/.cursor/mcp.json`.
- **src/store/skills/** – Cursor skills as `.md` files with YAML frontmatter (`name`, `description`). Each file is installed as `~/.cursor/skills/<stem>/SKILL.md`.

## Adding more

- **MCP**: Add a JSON file under `src/store/mcp-tools/<name>.json` with the server object to merge (e.g. `{"serverName": {"command": "...", "args": [], "env": {}}}`), and a `src/setup_<name>.py` that imports `src.lib` and calls `merge_mcp_server()` (see `setup_github.py` and `setup_postgres.py`).
- **Skills**: Add a `.md` file under `src/store/skills/` with `name` and `description` in the frontmatter. It will appear in the skills table on the next run.
