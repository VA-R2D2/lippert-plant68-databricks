# Databricks and Data Readiness Checklist

| Done | Item | What We Need | Owner | Notes |
| --- | --- | --- | --- | --- |
| [ ] | Databricks workspace | Access to 1 existing DEV workspace, or provision 1 new DEV workspace if needed. Do not create a duplicate if an existing workspace is available. |  |  |
| [ ] | On-premises SQL sources | Server/database details, required tables/views, schema documentation, approved SQL API endpoint URL, JSON records path, and access to SQL APIs for the pipeline into the lakehouse. |  |  |
| [ ] | Sample data | Source tables/views populated with approved sample data or sanitized extracts. Suggested scope: 1-2 weeks of representative data plus a current or simulated shift; confirm exact start date, end date, and timezone with the business owner. |  |  |
| [ ] | Databricks workspace permissions | Workshop team can create notebooks, pipelines, and compute within approved policies. |  |  |
| [ ] | Unity Catalog permissions | Read approved source data and create temporary tables/views and other required data objects in a designated DEV catalog/schema, including the agreed target Delta table for ingested sample data. |  |  |
| [ ] | Databricks secret scope | Confirm an approved secret scope and secret key name exist for the SQL API token or supported credential. Do not store the token value in this repo. |  |  |
| [x] | Managed MCP servers | Enable the Managed MCP Servers preview in the DEV workspace; confirm availability and customer approval. |  | Genie MCP endpoint created for the `Lippert Plant 68 Production Scheduling` space. |
| [x] | Databricks MCP authentication | Configure the supported OAuth flow and any required client credentials for the Foundry-to-Databricks connection. Keep credentials in approved secure storage; this is separate from UI/API sign-in. |  | Foundry-managed OAuth connector `foundrydatabricksmcp`; no client secret stored in this repo. |
| [x] | MCP connectivity | Validate an authenticated call from the intended Foundry connection to the Databricks MCP endpoint and confirm access to the intended data/tools. |  | Foundry toolbox `lippert68-production-toolbox` returned two read-only Genie tools through authenticated `tools/list`. |
| [ ] | KPIs and business rules | List the measures to build, with formulas, thresholds, source fields, expected sample results, and a business owner available to validate them. |  |  |
| [ ] | Agent reference documents | Approved SOPs/playbooks, owners, source URIs, approval status, and a metadata table/view for agent grounding validation. |  |  |
