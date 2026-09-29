# Session Prompts - September 30, 2026

Use these prompts in order for the next working session. Do not include passwords, tokens, client secrets, or customer data in chat.

## 1. Resume the Session

```text
Resume the Lippert Plant 68 Databricks and Microsoft Foundry session.

Use Azure subscription 4d052fa6-b5d1-4839-8f64-db2dc2ceb867, tenant 9c20a310-ca4c-464d-84a4-feea604f906d, and resource group VA-Fabric. Confirm the active subscription before making changes.

Use the existing resources. Do not create duplicate workspaces, Foundry projects, Genie spaces, connections, toolboxes, warehouses, volumes, or tables.

Existing resources:
- Databricks workspace: Lippert68
- Databricks host: https://adb-7405618852366175.15.azuredatabricks.net
- Databricks CLI profile: Lippert68
- Unity Catalog schema: lippert68.default
- Volume: /Volumes/lippert68/default/production_scheduling_data
- Genie space: Lippert Plant 68 Production Scheduling
- Genie space ID: 01f1bb820170162fa412ee4476fe31a2
- SQL warehouse: Serverless Starter Warehouse (b1260ba6d99db594)
- Foundry project: proj-default
- Foundry project endpoint: https://semanticsearchva.services.ai.azure.com/api/projects/proj-default
- Foundry MCP connection: lippert68-databricks-genie
- Foundry toolbox: lippert68-production-toolbox, version 1

First verify Azure authentication, Databricks authentication, the warehouse state, and Foundry connectivity. Report the current state before changing anything.
```

## 2. Validate the Data

```text
Verify the ten uploaded Excel workbooks still exist in /Volumes/lippert68/default/production_scheduling_data and confirm the ten Delta tables in lippert68.default are readable. Report table names and row counts. Do not overwrite or modify data.
```

Expected tables:

- `edit_open_jobs_1`
- `export_jobs_ids_database_import`
- `export_routes_ids_database_import`
- `job_history`
- `manage_part_sources_demand_plan_parameters`
- `max_job_id`
- `part_properties_demand_plan_parameters`
- `production_orders_planned_orders_to_be_firmed_each_week`
- `scm_part_properties_demand_plan_parameters`
- `setup_routes`

## 3. Validate Databricks MCP

```text
Validate the existing Databricks Genie MCP endpoint with an authenticated JSON-RPC tools/list request. Confirm it exposes only the query and polling tools and that both tools are read-only. Do not create a new Genie space.

Endpoint:
https://adb-7405618852366175.15.azuredatabricks.net/api/2.0/mcp/genie/01f1bb820170162fa412ee4476fe31a2
```

## 4. Validate Foundry MCP

```text
Validate the existing Microsoft Foundry toolbox MCP endpoint using Microsoft Entra authentication. Confirm the lippert68-databricks-genie connection succeeds and returns the two read-only Genie tools. Reuse the existing OAuth consent and do not create a new connection or toolbox.

Toolbox endpoint:
https://semanticsearchva.services.ai.azure.com/api/projects/proj-default/toolboxes/lippert68-production-toolbox/versions/1/mcp?api-version=v1
```

## 5. Run a Read-Only Analytics Test

```text
Through the Foundry toolbox, ask the Lippert Plant 68 Genie space for a concise overview of the available production-scheduling datasets. Require approval before the MCP call, run only read-only queries, and report the generated SQL and result summary. Do not update tables or create new data objects.
```

## 6. Continue the Business Analysis

```text
Use the existing Genie MCP tools to analyze production scheduling. Start with these questions:
1. How many production orders are planned to be firmed each week?
2. Summarize open jobs and job history by source file.
3. Which parts and routes have the highest activity?

Show assumptions, generated SQL, source tables, and any data-quality limitations. Keep every operation read-only.
```

## 7. End the Session

```text
End the session safely. Check all Databricks all-purpose clusters and SQL warehouses. Stop any running compute, then verify the Serverless Starter Warehouse reports STOPPED with zero active clusters. Do not delete the Genie space, MCP connection, Foundry toolbox, model deployments, tables, or volume.

Microsoft Foundry itself cannot be paused like a cluster. Its gpt-5 GlobalStandard and text-embedding-3-small Standard deployments are consumption-based and have no idle compute charge, so leave them intact.
```

## Verified MCP Links

- Databricks Genie MCP: `https://adb-7405618852366175.15.azuredatabricks.net/api/2.0/mcp/genie/01f1bb820170162fa412ee4476fe31a2`
- Foundry Toolbox MCP: `https://semanticsearchva.services.ai.azure.com/api/projects/proj-default/toolboxes/lippert68-production-toolbox/versions/1/mcp?api-version=v1`