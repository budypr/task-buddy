---
name: pg-ask
description: Answers Postgres questions and writes SQL using the Postgres MCP. Clarifies the request, discovers schema and relationships, applies parameterized queries and performance rules, outputs formatted SQL. Use when the user asks about their Postgres database, wants a query written or explained, or mentions PostgreSQL, SQL, schema, tables, or relationships.
mcp: postgres
---

# pg-ask

Answer Postgres questions and write SQL using the **Postgres MCP**. Prerequisite: Postgres MCP server configured and available (e.g. run `python3 src/setup_postgres.py`). If the tool is unavailable, tell the user to enable the Postgres MCP server.

## 1. Understand the request

Before writing any SQL:

- **Summarize** what the user is asking (e.g. list X, count Y by Z, find A that have no B).
- If anything is ambiguous (table/column names, filters, grouping, limits), ask **specific questions** and stay in a **feedback loop** until the request is clear. Do not assume table or column names.
- Proceed to schema discovery and query construction only when the intent is clear.

## 2. Understand relationships

Use the Postgres MCP (read-only) to discover schema and relationships:

- **Tables and columns:** `information_schema.tables`, `information_schema.columns`, or `pg_catalog` as appropriate.
- **Relationships:** `information_schema.table_constraints`, `information_schema.key_column_usage`, `information_schema.referential_constraints` to identify primary and foreign keys.

Use this to choose the right tables and join conditions. Avoid Cartesian products; respect FKs. Note primary/unique keys and common index targets for the query you will write.

## 3. Query quality and safety

- **Parameterized queries:** Use placeholders (e.g. `$1`, `$2`) for all user or variable input. Never concatenate values into SQL. Show the parameterized query and list parameters separately (e.g. "Parameters: $1 = ..., $2 = ...") so the user can bind values safely.
- **Limit result sets:** Apply a sensible `LIMIT` unless the request explicitly needs a full set (e.g. export, count). Document the default cap when showing the query.
- **Appropriate JOINs:** Express relationships with explicit `JOIN` ... `ON`. Prefer `INNER JOIN` for required relationships. Use `WHERE` only for filter conditions, not for joining tables.
- **Select only needed columns:** List exact columns or expressions. Do not use `SELECT *`.
- **Consider indexes:** Structure queries to use indexes: join on key columns, filter in `WHERE` on indexed columns where possible.

## 4. Performance

- **EXPLAIN for complex queries:** For non-trivial queries (multiple JOINs, subqueries, aggregations), suggest running `EXPLAIN (ANALYZE)` and interpreting the plan (sequential scans, missing indexes, high cost). Use this to refine the query or suggest indexes.
- **Avoid N+1:** Do not design "one query per row." Use a single query with JOINs, or batch with `IN (...)` / `= ANY($1::int[])`, or a LATERAL join.

## 5. Construct the query and show it (format)

Present SQL in a fenced code block with language `sql`. Apply these rules:

- **Keywords in UPPERCASE** (SELECT, FROM, WHERE, JOIN, ON, AND, OR, GROUP BY, ORDER BY, LIMIT, etc.).
- **Column alignment in SELECT:** Comma at end of previous line; column names/expressions aligned under the first.
- **Each JOIN on its own line, properly indented:** `FROM` and first table on one line; each `JOIN` indented one level under `FROM`; each `ON` indented one level under its `JOIN`.
- **Maximum line length 150 characters.** Break at logical places (after comma, after keyword).

**Indentation pattern:**

```text
  FROM <table> [alias]
       INNER JOIN <table> [alias]
           ON <condition>
       LEFT JOIN <table> [alias]
           ON <condition>
 WHERE ...
```

### Example 1 — SELECT with JOINs (parameterized)

```sql
SELECT u.id,
       u.email,
       u.created_at,
       p.display_name,
       r.name AS role_name
  FROM users u
       INNER JOIN profiles p
           ON p.user_id = u.id
       INNER JOIN roles r
           ON r.id = u.role_id
 WHERE u.active = TRUE
   AND u.created_at >= $1::date
 ORDER BY u.created_at DESC
 LIMIT $2;
```

Parameters: `$1` = start date (e.g. `CURRENT_DATE - INTERVAL '30 days'`), `$2` = limit (e.g. `100`).

### Example 2 — LEFT JOINs and GROUP BY

```sql
SELECT o.id,
       o.reference,
       o.total_cents,
       o.created_at,
       c.email AS customer_email,
       s.name AS status_name
  FROM orders o
       LEFT JOIN customers c
           ON c.id = o.customer_id
       LEFT JOIN order_statuses s
           ON s.id = o.status_id
 WHERE o.created_at BETWEEN $1::date AND $2::date
   AND o.status_id = ANY($3::int[])
 GROUP BY o.id, o.reference, o.total_cents, o.created_at, c.email, s.name
 ORDER BY o.total_cents DESC
 LIMIT 500;
```

Parameters: `$1` = start date, `$2` = end date, `$3` = array of status IDs.

### Example 3 — Subquery with JOINs

```sql
SELECT p.id,
       p.title,
       p.slug,
       p.published_at
  FROM posts p
       INNER JOIN users u
           ON u.id = p.author_id
 WHERE p.published_at IS NOT NULL
   AND EXISTS (
         SELECT 1
           FROM post_tags pt
                INNER JOIN tags t
                    ON t.id = pt.tag_id
          WHERE pt.post_id = p.id
            AND t.slug = $1
       )
 ORDER BY p.published_at DESC
 LIMIT $2;
```

Parameters: `$1` = tag slug (e.g. `'featured'`), `$2` = limit.
