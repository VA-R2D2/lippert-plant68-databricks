$ErrorActionPreference = 'Stop'

if (-not $env:MCP_ENDPOINT_URL) {
  Write-Error "MCP_ENDPOINT_URL is not set."
  exit 1
}

Write-Host "Validating MCP endpoint reachability..."
try {
  $response = Invoke-WebRequest -Uri $env:MCP_ENDPOINT_URL -Method Get -UseBasicParsing
  Write-Host "Status Code: $($response.StatusCode)"
} catch {
  $statusCode = $null

  if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
    $statusCode = $_.Exception.Response.StatusCode.value__
  }

  if ($statusCode -eq 401 -or $statusCode -eq 403) {
    Write-Warning "Endpoint is reachable but requires authentication. Validate OAuth credentials from the approved Foundry-to-Databricks connection."
    Write-Host "Status Code: $statusCode"
    exit 0
  }

  throw
}
