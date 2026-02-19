---
name: squash-this
description: Runs a structured development workflow ASK → PLAN → TECHNICAL DETAILS → IMPLEMENT with clarity checks and user confirmation. Use when the user wants a phased approach, structured workflow, ask-then-plan-then-implement, or to avoid assumptions before building.
mcp: github
---

# Squash-this

Structured workflow: **ASK → PLAN → TECHNICAL DETAILS → IMPLEMENT**. Do not skip phases. Do not assume—confirm with the user at each gate.

## Prerequisite: GitHub issue

Squash-this **requires a GitHub issue ID** (issue number or full reference). Do not start the workflow without it.

1. **Get the issue reference** from the user (e.g. `#42`, `42`, or owner/repo#42). Resolve **owner** and **repo** from the current workspace git remote when not given (parse `origin`; if the remote is not github.com or cannot be parsed, ask the user for owner and repo).
2. **Fetch the issue via GitHub MCP:** Use **mcp_github_get_issue** to retrieve the issue's **title**, **body** (description), and **comments**. Use this as the **primary context** for all phases (ASK, PLAN, TECHNICAL DETAILS, IMPLEMENT).
3. **Load context before Phase 1:** The issue title, description, and comments define the problem and constraints. Use them to research, summarize, and drive the workflow. If the issue cannot be fetched (e.g. GitHub MCP unavailable or invalid ID), ask the user to provide the issue reference or enable GitHub MCP.

## Solution standards

Every solution produced in PLAN, TECHNICAL DETAILS, and IMPLEMENT must adhere to:

- **SOLID** — Single responsibility, Open/closed, Liskov substitution, Interface segregation, Dependency inversion.
- **Scalability by design** — Assume growth in load, data, and features; avoid single-point bottlenecks and hidden limits.
- **Best-in-class code quality** — Readable, testable, maintainable; consistent style. Readable code over commented code: names explain intent; comments explain **why**, not what.
- **Fail fast, fail loud** — Validate early; surface errors immediately with clear messages; no silent failures or swallowed exceptions.
- **Separation of concerns** — Distinct layers/responsibilities (e.g. domain, application, infrastructure); no mixing.
- **Explicit over implicit** — Clear APIs, explicit configuration and dependencies; avoid magic and hidden behavior.
- **Security by design** — Auth, input validation, least privilege, and secure defaults considered from the start.

Apply these when evaluating options (PLAN), designing (TECHNICAL DETAILS), and implementing (IMPLEMENT).

## Phase 1: ASK

1. **Research** using the GitHub issue context (title, description, comments) plus the codebase, docs, and patterns.
2. **Summarize** what is clear and what is unclear or missing from the issue and codebase.
3. **Decision:**
   - If everything needed is clear and you are not assuming anything → state "Moving to PLAN" and proceed to Phase 2.
   - If anything is unclear or missing → ask the user specific questions. Stay in ASK until resolved, then proceed to PLAN.

## Phase 2: PLAN

1. Propose **at least 3 options** (or as many as make sense if the problem has fewer).
2. For each option give: short description, main steps, **pros**, **cons**.
3. Invite the user to pick one (or combine). Do not implement yet.

## Phase 3: TECHNICAL DETAILS

1. For the **chosen option**, spell out the implementation: files to add/change, key functions, data flow, dependencies, risks.
2. **Confirm with the user** explicitly (e.g. "Confirm to proceed to implementation?").
3. Only move to IMPLEMENT after the user confirms.

## Phase 4: IMPLEMENT

1. **Set up branch:**
   - **Assign the GitHub issue to the user:** Use **mcp_github_update_issue** with assignees set to the user's GitHub username (ask if unknown).
   - **Git:** Run `git fetch --all`, then create and checkout a new branch off the local default branch (e.g. `main` or `master`) with the format `{github_user}/{issue_number}-{short-descriptive-title}` (e.g. `ivan/42-add-user-login`). Use the user's GitHub username for `{github_user}` (from git config or ask if unknown).
2. **Write the implementation plan** to a folder:
   - Path: `{workspace root}/dev_agent_notes/{issue_id}-{short-descriptive-title}/`
   - Use the same short-descriptive-title as in the branch name (e.g. `42-add-user-login`, `17-refactor-payment-flow`).
   - Put the full detailed plan in a file there (e.g. `README.md` or `plan.md`).
3. **Execute** the plan: implement the solution (edit files, add tests, run commands) in agent mode. Follow the written plan.

## Summary

| Phase              | Exit condition                          |
|--------------------|----------------------------------------|
| ASK                | Clarity reached; no assumptions        |
| PLAN               | User has chosen (or merged) an option   |
| TECHNICAL DETAILS  | User confirmed the approach            |
| IMPLEMENT          | Plan written to `dev_agent_notes/`, then code done |
