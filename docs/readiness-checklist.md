# Databricks and Data Readiness Checklist

| Done | Item | What We Need | Owner | Notes |
| --- | --- | --- | --- | --- |
| [ ] | Databricks workspace | Access to 1 existing DEV workspace, or provision 1 new DEV workspace if needed. Do not create a duplicate if an existing workspace is available. |  |  |
| [ ] | On-premises SQL sources | Server/database details, required tables/views, schema documentation, and access to SQL APIs for the pipeline into the lakehouse. |  |  |
| [ ] | Sample data | Source tables/views populated with approved sample data or sanitized extracts. Suggested scope: 1-2 weeks of representative data plus a current or simulated shift; confirm exact dates and timezone with the business owner. |  |  |
| [ ] | Databricks workspace permissions | Workshop team can create notebooks, pipelines, and compute within approved policies. |  |  |
| [ ] | Unity Catalog permissions | Read approved source data and create temporary tables/views and other required data objects in a designated DEV catalog/schema. |  |  |
| [ ] | Managed MCP servers | Enable the Managed MCP Servers preview in the DEV workspace; confirm availability and customer approval. |  |  |
| [ ] | Databricks MCP authentication | Configure the supported OAuth flow and any required client credentials for the Foundry-to-Databricks connection. Keep credentials in approved secure storage; this is separate from UI/API sign-in. |  |  |
| [ ] | MCP connectivity | Validate an authenticated call from the intended Foundry connection to the Databricks MCP endpoint and confirm access to the intended data/tools. |  |  |
| [ ] | KPIs and business rules | List the measures to build, with formulas, thresholds, source fields, expected sample results, and a business owner available to validate them. |  |  |
| [ ] | Agent reference documents | Approved SOPs/playbooks and their owners for agent grounding. |  |  |
