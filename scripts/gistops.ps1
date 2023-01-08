#!/usr/bin/env powershell

Param(
    [Parameter(Mandatory=$False)]
    [string]$GitRepositoryDir = '.',

    [Parameter(Mandatory=$False)]
    [string]$GistopsImageRegistryPrefix = $env:GISTOPS_IMAGE_REGISTRY_PREFIX
)

if ([string]::IsNullOrWhitespace($GistopsImageRegistryPrefix)) {
    $GistopsImageRegistryPrefix = 'ghcr.io/dandens'
}

################
# Check Params #
################
# Run docker info
& 'docker.exe' info > $null
if ("$LastExitCode" -ne 0) {
    Write-Host `
      "Docker is not running or user `"$env:UserName`" is not allowed to access docker;"`
      "please ensure docker is accessible by user `"$env:UserName`" and rerun command"
    exit 1
}

if (-not (Test-Path -Path "$GitRepositoryDir\.git")) {
    Write-Host `
      "`"$GitRepositoryDir`" is not a git repository."`
      "Please provide path to a valid git repository"
    exit 1
}
$GitRepositoryDir = Resolve-Path -Path "$GitRepositoryDir"

##################
# Dockerize Jobs #
##################
function Run-Gistops {
    Param (
      [Parameter(Mandatory=$True)]
      [string]$GistopsImage,

      [Parameter(Mandatory=$False)]
      [string[]]$GistopsParameters = @()
    )

    $GistopsImageUri = "${GistopsImageRegistryPrefix}/$GistopsImage"
    if ([string]::IsNullOrWhitespace("$(docker image ls $GistopsImageUri --format '{{json . }}')")) {
        Write-Host "docker pull $GistopsImageUri > `$null"
        & docker pull $GistopsImageUri > $null
    }

    $GistopsContainerName = "gistops-$(-join ((65..90) + (97..122) | Get-Random -Count 10 | % {[char]$_}))"
    Write-Host "docker run --name `"${GistopsContainerName}`" --workdir `"/home/dandens/ws`" --volume `"${GitRepositoryDir}:/home/dandens/ws`" ${GistopsImageUri} ${GistopsParameters} > `$null"
    & docker run --name "${GistopsContainerName}" --workdir "/home/dandens/ws" --volume "${GitRepositoryDir}:/home/dandens/ws" $GistopsImageUri $GistopsParameters > $null

    $gistops_stdout=$(docker logs "$GistopsContainerName")

    & docker rm "$GistopsContainerName" > $null

    return $gistops_stdout
}

###############
# Run Gistops #
###############
# 1. analyze
Run-Gistops 'gistops-trufflehog:1133f19' @("gistops", ".")
$gists_git_ls_attr = Run-Gistops 'gistops-git-ls-attr:eab342b' @("gistops", "run")

# 2. convert
$gists_jupyter = Run-Gistops 'gistops-jupyter:31c649e' @(
  'gistops','run',"--event-base64=$gists_git_ls_attr")
$gists_pandoc = Run-Gistops 'gistops-pandoc:31c649e' @(
  'gistops','run',"--event-base64=['$gists_git_ls_attr','$gists_jupyter']")

# 3. publish
if ( -not ([string]::IsNullOrWhitespace($env:GISTOPS_JIRA_URL) -or 
           [string]::IsNullOrWhitespace($env:GISTOPS_JIRA_ACCESS_TOKEN)) ) {
    Run-Gistops 'gistops-jira:31c649e' @(
      'gistops','run',
      "--event-base64=$gists_pandoc",
      "--jira-url=$env:GISTOPS_JIRA_URL",
      "--jira-access-token=$env:GISTOPS_JIRA_ACCESS_TOKEN")
}

if ( -not ([string]::IsNullOrWhitespace($env:GISTOPS_CONFLUENCE_URL) -or 
           [string]::IsNullOrWhitespace($env:GISTOPS_CONFLUENCE_ACCESS_TOKEN)) ) {
    Run-Gistops 'gistops-confluence:31c649e' @(
      'gistops','run',
      "--event-base64=$gists_pandoc",
      "--confluence-url=$env:GISTOPS_CONFLUENCE_URL",
      "--confluence-access-token=$env:GISTOPS_CONFLUENCE_ACCESS_TOKEN")
}

# 4. report
if ( -not ([string]::IsNullOrWhitespace($env:GISTOPS_MSTEAMS_WEBHOOK_URL) -or 
           [string]::IsNullOrWhitespace($env:GISTOPS_MSTEAMS_REPORT_TITLE)) ) {
    Run-Gistops 'gistops-msteams:31c649e' @(
      'gistops','run',
      "--webhook-url=$env:GISTOPS_MSTEAMS_WEBHOOK_URL",
      "--report-title=$env:GISTOPS_MSTEAMS_REPORT_TITLE" )
}
