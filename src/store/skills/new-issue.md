---
name: new-issue
description: Create GitHub issues with required type labels (bug, feature, spike). Use when the user wants to open a new issue, file a bug, log a feature, or create a spike.
mcp: github
---

# New Issue

Use GitHub MCP to create issues. **Prerequisite:** GitHub MCP server enabled and authenticated. If GitHub MCP is not available, tell the user to enable the GitHub MCP server and set `GITHUB_PERSONAL_ACCESS_TOKEN`.

## Label (required)

Every issue must have **exactly one** of:

- `bug` — defect, regression, incorrect behavior
- `feature` — new capability or enhancement
- `spike` — investigation, exploration, proof-of-concept

If the user does not specify a type, ask which label applies before creating the issue.

## Issue format

**Title:** Short, imperative, no trailing period (e.g. "Add login form validation", "Fix timezone in report export").

**Body (template):** When writing the issue body, use icons on section headers. Structure:

- **📖 Description:** Context and background. Write as much detail as needed to thoroughly explain the ticket (why it exists, background, constraints, links — whatever is relevant).
- **✅ Acceptance criteria / Tasks:** Bullet list of what "done" looks like (optional for spikes).
- **🔧 Implementation notes:** Technical notes, approach, or implementation hints (optional).

Use the template when the user does not provide a full body.

## Repository (owner / repo)

**Create the issue in the repo the user is working in.** Determine owner and repo from the current workspace:

- From the workspace **git remote** (e.g. `origin`): parse `https://github.com/owner/repo` or `git@github.com:owner/repo.git` to get `owner` and `repo`.
- If the workspace is not a git repo or has no GitHub remote, ask the user for owner and repo.

Do not ask for owner/repo when they can be inferred from the project.

## Workflow

1. Resolve **owner** and **repo** from the current repo's git remote; only ask if unknown.
2. Confirm **label**: bug, feature, or spike.
3. Draft **title** and **body** from user input; fill from template if needed.
4. Call the GitHub MCP tool to create the issue with that single label.
