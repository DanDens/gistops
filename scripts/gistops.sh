#!/bin/bash
set -e

################
# Check Params #
################
if ! docker info >/dev/null 2>&1; then
    echo \
    "Docker is not running or user \"$USER\" is not allowed to access docker; " \
    "please ensure docker is accessible and rerun command"
    exit 1
fi

GIT_REPOSITORY_DIR=$(realpath "${1:-.}")
if ! [ -d "$GIT_REPOSITORY_DIR/.git" ]; then
    echo "\"$GIT_REPOSITORY_DIR\" is not a git root directory."\
      "Please provide path to a git root directory."
    exit 1
fi

[[ -n "${GISTOPS_IMAGE_REGISTRY_PREFIX}" ]] || GISTOPS_IMAGE_REGISTRY_PREFIX="ghcr.io/dandens"

##################
# Dockerize Jobs #
##################
run_gistops() {
  local GISTOPS_IMAGE_URI="${GISTOPS_IMAGE_REGISTRY_PREFIX}/$1"
  local GISTOPS_CONTAINER_NAME="gistops-$(cat /proc/sys/kernel/random/uuid | sed 's/[-]//g' | head -c 10)"
  
  if [ -z "$(docker image ls $GISTOPS_IMAGE_URI --format '{{json . }}')" ]; 
  then
      echo "docker pull $GISTOPS_IMAGE_URI > /dev/null"
      docker pull "$GISTOPS_IMAGE_URI" > /dev/null 
  fi 

  echo "docker run --name '$GISTOPS_CONTAINER_NAME' --workdir '/home/dandens/ws' --volume '$GIT_REPOSITORY_DIR:/home/dandens/ws' $GISTOPS_IMAGE_URI ${@:2} > /dev/null"
  docker run \
  --name "$GISTOPS_CONTAINER_NAME" \
  --workdir "/home/dandens/ws" \
  --volume "$GIT_REPOSITORY_DIR:/home/dandens/ws" \
  "$GISTOPS_IMAGE_URI" \
  ${@:2} > /dev/null

  gistops_stdout=$(docker logs "$GISTOPS_CONTAINER_NAME")

  docker rm "$GISTOPS_CONTAINER_NAME" > /dev/null
}

###############
# Run Gistops #
###############
# 1. analyze
run_gistops 'gistops-trufflehog:b22a808' 'gistops' '.'
run_gistops 'gistops-git-ls-attr:a22694b' 'gistops' 'run'
gists_git_ls_attr="$gistops_stdout"

# 2. convert
run_gistops 'gistops-jupyter:513f9c0' 'gistops' 'run' "--event-base64=$gists_git_ls_attr"
gists_jupyter="$gistops_stdout"
run_gistops 'gistops-pandoc:3f14c69' 'gistops' 'run' "--event-base64=['$gists_git_ls_attr','$gists_jupyter']"
gists_pandoc="$gistops_stdout"

# 3. publish
if [[ -n "$GISTOPS_JIRA_URL" ]] && [[ -n "$GISTOPS_JIRA_ACCESS_TOKEN" ]]; then
    run_gistops 'gistops-jira:9f50ec1' 'gistops' 'run' \
      "--event-base64=$gists_pandoc" \
      "--jira-url=$GISTOPS_JIRA_URL" \
      "--jira-access-token=$GISTOPS_JIRA_ACCESS_TOKEN"
fi

if [[ -n "$GISTOPS_CONFLUENCE_URL" ]] && [[ -n "$GISTOPS_CONFLUENCE_ACCESS_TOKEN" ]]; then
    run_gistops 'gistops-confluence:3f14c69' 'gistops' 'run' \
      "--event-base64=$gists_pandoc" \
      "--confluence-url=$GISTOPS_CONFLUENCE_URL" \
      "--confluence-access-token=$GISTOPS_CONFLUENCE_ACCESS_TOKEN"
fi

# 4. report
if [[ -n "$GISTOPS_MSTEAMS_WEBHOOK_URL" ]] && [[ -n "$GISTOPS_MSTEAMS_REPORT_TITLE" ]]; then
    run_gistops 'gistops-msteams:b22a808' 'gistops' 'run' \
      "--webhook-url=$GISTOPS_MSTEAMS_WEBHOOK_URL" \
      "--report-title=$GISTOPS_MSTEAMS_REPORT_TITLE"
fi
