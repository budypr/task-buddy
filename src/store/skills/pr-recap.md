---
name: pr-recap
description: Generates pull request summaries with five required parts: what changed, why it changed, impact analysis, visual summaries (architecture and change-impact diagrams), and testing steps. Infers context from the current git branch; uses GitHub MCP to find the PR for the branch when available. Use when the user asks for a PR summary, PR description, PR recap, draft a pull request description, or write up a pull request.
mcp: github
---

# pr-recap

Generate a PR recap (summary) in the exact structure below. **Prerequisite:** GitHub MCP enabled for PR lookup. If GitHub MCP is unavailable, infer from git only and tell the user they can enable GitHub MCP to link the branch to an existing PR.

## When to use

Apply this skill when the user:
- Asks for a PR summary, PR description, PR recap, or to "write up" a pull request
- Wants to draft or polish a pull request description

## Workflow

Do these steps in order:

1. **Resolve owner and repo** — From the workspace git remote (e.g. `origin`), parse `https://github.com/owner/repo` or `git@github.com:owner/repo.git`. If not a git repo or no remote, ask the user for owner and repo.
2. **Get current branch** — Run `git branch --show-current`.
3. **Find PR for this branch** — Call GitHub MCP `list_pull_requests` with `head` = `owner:branch` (e.g. `owner:feature/login`). If a PR exists, use its title, body, and diff to enrich the recap.
4. **Infer changes from git** — Run `git diff main...HEAD` (or `origin/main...HEAD` / the repo’s default branch). Optionally run `git log main..HEAD --oneline`. Use the diff and commit messages to fill the five sections.
5. **If no git or no diff** — Ask the user for a short summary of what changed, then produce the recap from that.
6. **Produce the recap** — Output the five sections below using the exact headings and rules. Use the **Output format** template as the structure for your response.

## Output format

Produce the recap in this structure. Use these section headings exactly. Testing steps (section 5) are required.

```markdown
### 1. What changed

[Bullet list of what was added, changed, or removed. Include files, modules, APIs, UI, config. Reference paths or component names where helpful.]

### 2. Why it changed

[Motivation and context: problem solved, ticket/issue link, product or technical rationale. Assume the reader does not know the history.]

### 3. Impact analysis

[Who or what is affected: downstream callers, other services, DB schema, API contracts, UX, performance, security. Explicitly call out breaking changes, migration needs, rollout considerations.]

### 4. Visual summaries

[Generate Mermaid or similar diagrams when the change warrants it. Omit for trivial one-file changes.]

**4a. Architecture diagrams** (when the PR touches structure or integration):
- **Component relationship** — How new or changed components relate to existing ones (boxes and edges).
- **Data flow** — Where data enters, is transformed, and exits (e.g. request → service → DB → response).
- **Dependency graphs** — What depends on what (modules, packages, layers).
- **File structure** — Relevant part of the repo tree (new/changed dirs and key files).

**4b. Change impact diagrams** (when the PR changes behavior or UX):
- **Before/after comparisons** — State or flow before vs after.
- **Affected areas** — Which parts of the system or UI are touched.
- **User flow changes** — How the user’s path through the product changes (steps, screens, decisions).

### 5. Testing steps (required)

[Always include this section. Steps must be user-facing and actionable.]

- **If the PR includes frontend/UI:** Write **manual UI test** steps. Use numbered steps: where to go, what to click or enter, what the user should see (e.g. "1. Open X. 2. Click Y. 3. Expect Z.").
- **If the PR is backend-only:** Write **code snippets** (e.g. curl, script, or test harness) that demonstrate the new or changed behavior (e.g. call the new API, assert response or side effect). Snippets should be copy-paste runnable where possible.
```

## Rules

- **PR title:** Short, descriptive, no trailing period. Suggest one at the top of the recap if the user did not provide it.
- **Tone:** Assume the reviewer does not know the branch. Be specific. Mention breaking changes and risks in Impact analysis.
- **Diagrams:** Include only when they add value (structure, integration, or behavior change). Omit for trivial changes.
- **Testing:** Section 5 is mandatory. Every recap must have actionable testing steps or runnable snippets.

## Example (shape of output)

**Title:** Add save-draft for report editor

**1. What changed** — New `ReportDraft` model and migration; `POST/GET /api/reports/:id/drafts`. Report editor: "Save draft" button and "Resume draft" on load. Files: `server/models/report_draft.py`, `server/routes/drafts.py`, `client/pages/ReportEditor.tsx`, `client/hooks/useReportDraft.ts`.

**2. Why it changed** — Fixes #42. Users had no way to leave the editor without losing work. Drafts are per-user, per-report; publishing replaces the published report.

**3. Impact analysis** — New API only; no breaking changes. New table; migration additive. Frontend is the only consumer. Feature-flag `report_drafts` for rollout.

**4. Visual summaries** — Component relationship (Editor → useDraft → API/DraftAPI → DB); data flow sequence (User → Editor → DraftAPI → DB); file structure; before/after user flow (leave = lose work vs save draft / resume).

**5. Testing steps** — (1) Open editor, edit, click Save draft → expect toast "Draft saved." (2) Leave and re-open same report → expect draft loaded and "Resuming draft." (3) Publish → expect report in list. (4) As another user, open same report → expect no draft. Backend: `curl -X POST .../drafts` and `curl .../drafts/latest` with expected 200/404.
