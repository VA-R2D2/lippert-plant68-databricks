# Prerequisites

## Required Access

- GitHub repository access.
- Databricks DEV workspace access.
- Permission to create notebooks.
- Permission to create or use approved compute.
- Unity Catalog DEV catalog/schema access.
- Access to approved SQL source APIs or sanitized extracts.
- Databricks secret scope access for the SQL API token or supported API credential.
- Approval to use the Managed MCP Servers preview.
- Foundry-managed OAuth access to the Databricks Genie MCP integration.
- Foundry User access to use the toolbox and Foundry Project Manager access to manage its connection.

## Required Information

- Databricks workspace URL.
- Microsoft Foundry project endpoint.
- Databricks Genie space MCP endpoint.
- Foundry MCP connection and toolbox names.
- DEV catalog name.
- DEV schema name.
- Target Delta table name for ingested sample data.
- SQL source server/database names.
- Required source tables/views.
- Approved list of source objects included in the sample-data extract.
- Approved SQL API endpoint URL for ingestion.
- JSON response path that contains the record array, for example `data` or `result.rows`.
- Sample data date range and timezone.
- Databricks secret scope name and secret key name for the SQL API token. Do not store the token itself in this repo.
- KPI definitions and expected sample results.
- Approved SOPs/playbooks for agent grounding.
- Reference-document metadata table or view with `document_name`, `owner`, `source_uri`, and `approval_status` columns.

## Ingestion Notebook Inputs

The notebook `notebooks/03_ingest_onprem_sql_api.py` requires these Databricks widget values:

| Widget | Description | Example |
| --- | --- | --- |
| `source_api_url` | Approved on-prem SQL API endpoint URL | `https://approved-api-host.example.com/api/source-data` |
| `target_catalog` | Unity Catalog DEV catalog | `dev_catalog` |
| `target_schema` | Unity Catalog DEV schema | `workshop_schema` |
| `target_table` | Delta table to overwrite with approved sample data | `approved_sample_source_data` |
| `secret_scope` | Databricks secret scope containing the API token | `approved-secret-scope` |
| `token_secret_key` | Secret key name for the API token | `sql-api-token` |
| `start_date` | Start of approved sample-data window | `2026-09-13` |
| `end_date` | End of approved sample-data window | `2026-09-27` |
| `timezone` | Business-approved timezone for the sample window | `America/Chicago` |
| `records_json_path` | Dot-path to the JSON array in the API response | `data` |
| `reference_document_table` | Table or view containing approved agent-grounding document metadata | `dev_catalog.workshop_schema.approved_reference_documents` |

## Notebook Sequence

1. `notebooks/01_workspace_smoke_test.py`
2. `notebooks/02_unity_catalog_permissions.py`
3. `notebooks/03_ingest_onprem_sql_api.py`
4. `notebooks/04_sample_data_profile.py`
5. `notebooks/05_kpi_validation.py`
6. `notebooks/06_agent_grounding_validation.py`

## Do Not Commit

- Passwords.
- Tokens.
- Client secrets.
- Raw production data.
- Unsanitized customer data.
- Private connection strings.
