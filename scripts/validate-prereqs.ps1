$ErrorActionPreference = 'Stop'

Write-Host "Validating local prerequisites..."

$requiredVars = @(
  "DATABRICKS_HOST",
  "DATABRICKS_CATALOG",
  "DATABRICKS_SCHEMA",
  "DATABRICKS_TARGET_TABLE",
  "REFERENCE_DOCUMENT_TABLE",
  "SQL_SOURCE_NAME",
  "SQL_DATABASE_NAME",
  "SQL_REQUIRED_OBJECTS",
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
$placeholders = @()

foreach ($var in $requiredVars) {
  $value = [Environment]::GetEnvironmentVariable($var)

  if (-not $value) {
    Write-Warning "Missing environment variable: $var"
    $missing += $var
  } else {
    Write-Host "Found: $var"

    if (
      $value -match "xxxxxxxx" -or
      $value -match "example\.com" -or
      $value -match "^your-" -or
      $value -match "source_system_name" -or
      $value -match "database_name" -or
      $value -match "approved-secret-scope" -or
      $value -match "sql-api-token"
    ) {
      $placeholders += $var
    }
  }
}

if ($missing.Count -gt 0) {
  Write-Error "Missing required environment variables: $($missing -join ', ')"
  exit 1
}

if ($placeholders.Count -gt 0) {
  Write-Error "Replace placeholder values before the workshop: $($placeholders -join ', ')"
  exit 1
}

Write-Host "Prerequisite validation complete."
