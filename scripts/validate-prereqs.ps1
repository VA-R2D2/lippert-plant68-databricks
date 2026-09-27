$ErrorActionPreference = 'Stop'

Write-Host "Validating local prerequisites..."

$requiredVars = @(
  "DATABRICKS_HOST",
  "DATABRICKS_CATALOG",
  "DATABRICKS_SCHEMA",
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
