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
4. Confirm the SQL API token or credential is stored in the approved Databricks secret scope.
5. Run the validation scripts in `scripts`.
6. Import or sync notebooks from `notebooks` into the Databricks DEV workspace.
7. Populate notebook widgets from `configs/example.env` and `docs/prerequisites.md`.
8. Track gaps as GitHub issues using the readiness issue template.

## Key Files

| Path | Purpose |
| --- | --- |
| `docs/readiness-checklist.md` | Main workshop readiness checklist |
| `docs/developer-runbook.md` | Step-by-step workflow for developers during the session |
| `docs/prerequisites.md` | Access, tooling, and information needed before the session |
| `docs/session-prompts-2026-09-30.md` | Copy-ready prompts for the September 30 follow-up session |
| `docs/kpi-template.md` | Template for KPI and business-rule definitions |
| `configs/example.env` | Non-secret configuration example |
| `scripts/validate-prereqs.ps1` | Local prerequisite validation |
| `scripts/validate-mcp-connectivity.ps1` | MCP endpoint reachability validation |
| `notebooks/03_ingest_onprem_sql_api.py` | Template for ingesting on-prem SQL API data into Delta/Unity Catalog |
| `notebooks` | Databricks smoke-test and validation notebooks |

## Notebook Order

1. `notebooks/01_workspace_smoke_test.py`
2. `notebooks/02_unity_catalog_permissions.py`
3. `notebooks/03_ingest_onprem_sql_api.py`
4. `notebooks/04_sample_data_profile.py`
5. `notebooks/05_kpi_validation.py`
6. `notebooks/06_agent_grounding_validation.py`

## Customer Handoff Checklist

- Replace sample values in `configs/example.env` with customer-approved non-secret values.
- Confirm all secrets are stored only in the approved Databricks secret scope.
- Confirm the DEV workspace, catalog, schema, compute policy, and MCP preview approval.
- Confirm source data is approved sample or sanitized data only.
- Confirm open blockers are tracked as GitHub issues before the session starts.

## Security

Do not commit credentials, tokens, client secrets, connection strings, customer data, production extracts, or unsanitized data. Use approved secure storage for secrets and approved sample or sanitized data only.
