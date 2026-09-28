param(
  [Parameter(Mandatory = $true)]
  [string]$RepoUrl,

  [string]$RemoteName = "origin",

  [string]$Branch = "main"
)

$ErrorActionPreference = 'Stop'

function Fail($Message) {
  Write-Error $Message
  exit 1
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  Fail "Git is not installed or is not available on PATH."
}

$insideWorkTree = git rev-parse --is-inside-work-tree 2>$null
if ($insideWorkTree -ne "true") {
  Fail "Run this script from inside the local repository folder."
}

if ($RepoUrl -notmatch '^https://github\.com/.+/.+(\.git)?$') {
  Fail "RepoUrl must look like https://github.com/owner/repo-name.git"
}

$currentBranch = git branch --show-current
if (-not $currentBranch) {
  Fail "Could not determine the current Git branch."
}

if ($currentBranch -ne $Branch) {
  Write-Host "Current branch is '$currentBranch'. Renaming it to '$Branch'."
  git branch -M $Branch
}

$status = git status --porcelain
if ($status) {
  Fail "There are uncommitted changes. Commit or stash them before pushing."
}

$existingRemote = git remote
if ($existingRemote -contains $RemoteName) {
  Write-Host "Updating remote '$RemoteName' to $RepoUrl"
  git remote set-url $RemoteName $RepoUrl
} else {
  Write-Host "Adding remote '$RemoteName' as $RepoUrl"
  git remote add $RemoteName $RepoUrl
}

Write-Host "Checking remote access..."
$remoteCheck = git ls-remote --heads $RemoteName 2>&1
if ($LASTEXITCODE -ne 0) {
  Write-Host $remoteCheck
  Fail "GitHub repo was not reachable. Confirm the repo exists and that you have access: $RepoUrl"
}

Write-Host "Pushing branch '$Branch' to '$RemoteName'..."
git push -u $RemoteName $Branch

Write-Host "Push complete."
