# Databricks Vibe Coding Readiness

This repository contains the readiness checklist, validation scripts, Databricks notebooks, and setup guidance for a Databricks vibe coding session.

## Goals

- Confirm Databricks DEV workspace readiness.
- Validate access to approved SQL sources and sample data.
- Validate Unity Catalog permissions.
- Validate Databricks MCP connectivity.
- Capture KPIs, formulas, thresholds, and business rules.
- Provide approved SOPs and playbooks for agent grounding.

## Developer Setup

1. Clone this repo.
2. Review `docs/prerequisites.md`.
3. Copy values from `configs/example.env` into local environment variables or an approved secret store.
4. Run the validation scripts in `scripts`.
5. Import or sync notebooks from `notebooks` into the Databricks DEV workspace.
6. Track gaps as GitHub issues using the readiness issue template.

## Key Files

| Path | Purpose |
| --- | --- |
| `docs/readiness-checklist.md` | Main workshop readiness checklist |
| `docs/prerequisites.md` | Access, tooling, and information needed before the session |
| `docs/kpi-template.md` | Template for KPI and business-rule definitions |
| `configs/example.env` | Non-secret configuration example |
| `scripts/validate-prereqs.ps1` | Local prerequisite validation |
| `scripts/validate-mcp-connectivity.ps1` | MCP endpoint reachability validation |
| `notebooks` | Databricks smoke-test and validation notebooks |

## Security

Do not commit credentials, tokens, client secrets, connection strings, customer data, production extracts, or unsanitized data. Use approved secure storage for secrets and approved sample or sanitized data only.
