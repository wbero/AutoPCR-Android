<#
.SYNOPSIS
Auto upload script for AutoPCR Android project to GitHub

.DESCRIPTION
This script initializes git repository, adds files, commits and pushes to GitHub repository.
Please make sure git is installed and GitHub credentials are configured before use.

.PARAMETER RepoUrl
GitHub repository URL, for example: https://github.com/yourusername/autopcr-android.git

.EXAMPLE
.\upload_to_github.ps1 -RepoUrl https://github.com/yourusername/autopcr-android.git

.NOTES
Author: AutoPCR Android Porting Team
License: CC BY-NC-SA 4.0
#>

param(
    [Parameter(Mandatory=$true, HelpMessage="GitHub Repository URL")]
    [string]$RepoUrl
)

# Check if git is installed
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "git is not installed. Please install git first."
    exit 1
}

# Check if current directory is already a git repository
if (-not (Test-Path .git)) {
    Write-Host "Initializing git repository..."
    git init
    if ($LASTEXITCODE -ne 0) {
        Write-Error "git init failed"
        exit 1
    }
}

# Check and configure git user identity
Write-Host "Checking git user identity..."
$gitUserEmail = git config user.email
$gitUserName = git config user.name

if (-not $gitUserEmail -or -not $gitUserName) {
    Write-Host "Git user identity not configured. Please enter your GitHub credentials:"
    $gitUserName = Read-Host -Prompt "Enter your GitHub username"
    $gitUserEmail = Read-Host -Prompt "Enter your GitHub email"
    
    Write-Host "Setting git user identity..."
    git config user.name "$gitUserName"
    git config user.email "$gitUserEmail"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to set git user identity"
        exit 1
    }
}

# Add remote repository
Write-Host "Adding remote repository: $RepoUrl"
git remote add origin $RepoUrl
if ($LASTEXITCODE -ne 0) {
    # If remote already exists, try to update
    Write-Host "Remote repository already exists, trying to update..."
    git remote set-url origin $RepoUrl
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to set remote repository"
        exit 1
    }
}

# Add files
Write-Host "Adding files to staging area..."
git add .
if ($LASTEXITCODE -ne 0) {
    Write-Error "git add failed"
    exit 1
}

# Commit files
Write-Host "Committing files..."
git commit -m "Initial commit: AutoPCR Android Port"
if ($LASTEXITCODE -ne 0) {
    Write-Error "git commit failed"
    exit 1
}

# Push files
Write-Host "Pushing files to GitHub..."
git push -u origin main
if ($LASTEXITCODE -ne 0) {
    Write-Error "git push failed. Please check your GitHub credentials and network connection."
    exit 1
}

Write-Host ""
Write-Host "✅ Project successfully uploaded to GitHub!"
Write-Host "Repository URL: $RepoUrl"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Visit GitHub repository to view uploaded files"
Write-Host "2. Set repository description and tags on GitHub"
Write-Host "3. Invite other developers to contribute"
Write-Host ""
Write-Host "Thank you for using AutoPCR Android Port!"
