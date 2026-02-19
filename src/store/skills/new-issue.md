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
- **✅ Acceptance criteria / Tasks:** Checkbox list of what "done" looks like. Use GitHub task list syntax: one unchecked checkbox per criterion, e.g. `- [ ] User can save draft` or `- [ ] API returns 404 when resource is missing`. For spikes, other criteria are optional but at least the doc checkbox (see Spikes) is required.
- **🔧 Implementation notes:** Technical notes, approach, or implementation hints (optional).

Use the template when the user does not provide a full body.

## Spikes

For issues labeled `spike`:

- Include in the body: **📝 Output:** Final research, plan, and implementation notes go in the `dev_agent_notes/` folder (or the project’s designated output folder).
- In **Acceptance criteria / Tasks**, include the checkbox: `- [ ] Document findings and implementation plan in dev_agent_notes`.

## Repository (owner / repo)

**Create the issue in the repo the user is working in.** Determine owner and repo from the current workspace:

- From the workspace **git remote** (e.g. `origin`): parse `https://github.com/owner/repo` or `git@github.com:owner/repo.git` to get `owner` and `repo`. If the remote URL is not github.com (e.g. GitLab or another host), ask the user for the GitHub owner and repo.
- If the workspace is not a git repo or has no GitHub remote, ask the user for owner and repo.

Do not ask for owner/repo when they can be inferred from the project.

## Workflow

1. Resolve **owner** and **repo** from the current repo's git remote; only ask if unknown.
2. Confirm **label**: bug, feature, or spike.
3. Draft **title** and **body** from user input; fill from template if needed.
4. Call **mcp_github_create_issue** with owner, repo, title, body, and labels (exactly one: the type label). Add assignees or milestone only if the user specifies them.
