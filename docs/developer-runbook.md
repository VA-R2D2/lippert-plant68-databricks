# Developer Runbook

Use this runbook after the repository is published and each developer has repository access.

## 1. Clone the Repository

```powershell
git clone https://github.com/ORG/databricks-vibe-coding-readiness.git
cd databricks-vibe-coding-readiness
```

Replace `ORG` with the GitHub organization or account that owns the repository.

## 2. Review Required Inputs

Read these files before running anything:

- `docs/prerequisites.md`
- `docs/readiness-checklist.md`
- `configs/example.env`

## 3. Set Local Environment Variables

Use customer-approved non-secret values. Do not store real credentials in this repo.

```powershell
$env:DATABRICKS_HOST="https://adb-xxxxxxxxxxxxxxxx.x.azuredatabricks.net"
$env:DATABRICKS_CATALOG="dev_catalog"
$env:DATABRICKS_SCHEMA="workshop_schema"
$env:DATABRICKS_TARGET_TABLE="approved_sample_source_data"
$env:REFERENCE_DOCUMENT_TABLE="dev_catalog.workshop_schema.approved_reference_documents"
$env:SQL_SOURCE_NAME="source_system_name"
$env:SQL_DATABASE_NAME="database_name"
$env:SQL_SOURCE_API_URL="https://approved-api-host.example.com/api/source-data"
$env:SQL_RECORDS_JSON_PATH="data"
$env:SAMPLE_DATA_START_DATE="2026-09-13"
$env:SAMPLE_DATA_END_DATE="2026-09-27"
$env:SAMPLE_DATA_TIMEZONE="America/Chicago"
$env:DATABRICKS_SECRET_SCOPE="approved-secret-scope"
$env:DATABRICKS_TOKEN_SECRET_KEY="sql-api-token"
$env:MCP_ENDPOINT_URL="https://your-databricks-mcp-endpoint"
```

## 4. Validate Local Readiness

```powershell
.\scripts\validate-prereqs.ps1
.\scripts\validate-mcp-connectivity.ps1
```

If a check fails, open a GitHub issue using the `Readiness Item` template.

## 5. Prepare Databricks

Confirm the developer can:

- Open the approved DEV workspace.
- Attach to approved compute.
- Create or run notebooks.
- Use the designated DEV catalog and schema.
- Read approved sample data or call the approved SQL API.
- Write the target Delta table in the designated DEV schema.
- Access the Databricks secret scope and secret key name for the SQL API credential.

## 6. Run Notebooks in Order

Run these notebooks in the Databricks DEV workspace:

1. `notebooks/01_workspace_smoke_test.py`
2. `notebooks/02_unity_catalog_permissions.py`
3. `notebooks/03_ingest_onprem_sql_api.py`
4. `notebooks/04_sample_data_profile.py`
5. `notebooks/05_kpi_validation.py`
6. `notebooks/06_agent_grounding_validation.py`

## 7. Widget Mapping

Use this mapping when filling Databricks notebook widgets:

| Notebook Widget | Source Value |
| --- | --- |
| `catalog` | `DATABRICKS_CATALOG` |
| `schema` | `DATABRICKS_SCHEMA` |
| `source_api_url` | `SQL_SOURCE_API_URL` |
| `target_catalog` | `DATABRICKS_CATALOG` |
| `target_schema` | `DATABRICKS_SCHEMA` |
| `target_table` | `DATABRICKS_TARGET_TABLE` |
| `secret_scope` | `DATABRICKS_SECRET_SCOPE` |
| `token_secret_key` | `DATABRICKS_TOKEN_SECRET_KEY` |
| `start_date` | `SAMPLE_DATA_START_DATE` |
| `end_date` | `SAMPLE_DATA_END_DATE` |
| `timezone` | `SAMPLE_DATA_TIMEZONE` |
| `records_json_path` | `SQL_RECORDS_JSON_PATH` |
| `source_table` | Fully qualified target table, for example `dev_catalog.workshop_schema.approved_sample_source_data` |
| `reference_document_table` | `REFERENCE_DOCUMENT_TABLE` |

For KPI validation, populate `kpi_name`, `kpi_sql_expression`, and `expected_result` from the completed KPI template in `docs/kpi-template.md`.

## 8. Session Ready Criteria

The repo is ready for the vibe coding session when:

- All readiness checklist items have owners.
- Required notebook widgets are populated.
- The ingestion notebook writes approved sample data to the target Delta table.
- The sample profile notebook displays row counts and schema.
- KPI definitions have formulas, thresholds, source fields, and expected sample results.
- Agent grounding documents have approved owners and source locations.
- MCP connectivity and authentication have been validated.
- Open blockers are tracked as GitHub issues.
