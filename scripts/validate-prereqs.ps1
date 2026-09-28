$ErrorActionPreference = 'Stop'

Write-Host "Validating local prerequisites..."

$requiredVars = @(
  "DATABRICKS_HOST",
  "DATABRICKS_CATALOG",
  "DATABRICKS_SCHEMA",
  "DATABRICKS_TARGET_TABLE",
  "SQL_SOURCE_API_URL",
  "SQL_RECORDS_JSON_PATH",
  "SAMPLE_DATA_START_DATE",
  "SAMPLE_DATA_END_DATE",
  "SAMPLE_DATA_TIMEZONE",
  "DATABRICKS_SECRET_SCOPE",
  "DATABRICKS_TOKEN_SECRET_KEY",
  "MCP_ENDPOINT_URL"
)

$missing = @()

foreach ($var in $requiredVars) {
  if (-not [Environment]::GetEnvironmentVariable($var)) {
    Write-Warning "Missing environment variable: $var"
    $missing += $var
  } else {
    Write-Host "Found: $var"
  }
}

if ($missing.Count -gt 0) {
  Write-Error "Missing required environment variables: $($missing -join ', ')"
  exit 1
}

Write-Host "Prerequisite validation complete."
