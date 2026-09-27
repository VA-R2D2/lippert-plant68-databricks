$ErrorActionPreference = 'Stop'

if (-not $env:MCP_ENDPOINT_URL) {
  Write-Error "MCP_ENDPOINT_URL is not set."
  exit 1
}

Write-Host "Validating MCP endpoint reachability..."
$response = Invoke-WebRequest -Uri $env:MCP_ENDPOINT_URL -Method Get -UseBasicParsing
Write-Host "Status Code: $($response.StatusCode)"
