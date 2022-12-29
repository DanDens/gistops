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

if ! [ $# -ge 1 ]; then 
    echo "No job provided, use either trufflehog, git-ls-attr, git-mirror, pandoc, confluence, jira or jupyter"
    exit 1
fi
GISTOPS_JOB="$1"

GISTOPS_GIT_ROOT=$(realpath "${2:-.}")
if ! [ -d "$GISTOPS_GIT_ROOT/.git" ]; then
    echo "\"$GISTOPS_GIT_ROOT\" is not a git root directory."\
      "Please provide path to a git root directory."
    exit 1
fi

[[ -n "${GISTOPS_IMAGE_REGISTRY_PREFIX}" ]] || GISTOPS_IMAGE_REGISTRY_PREFIX="ghcr.io/dandens"

# Create random container name
GISTOPS_CONTAINER_NAME="gistops-$(cat /proc/sys/kernel/random/uuid | sed 's/[-]//g' | head -c 10)"

########
# Jobs #
########
trufflehog() {
  docker run \
  --name "$GISTOPS_CONTAINER_NAME" \
  --workdir "/home/dandens/ws" \
  --volume "$GISTOPS_GIT_ROOT:/home/dandens/ws" \
  "${GISTOPS_IMAGE_REGISTRY_PREFIX}/gistops-trufflehog:b22a808" \
  gistops . "$@"
}

git_mirror() {
  docker run \
  --name "$GISTOPS_CONTAINER_NAME" \
  --workdir "/home/dandens/ws" \
  --volume "$GISTOPS_GIT_ROOT:/home/dandens/ws" \
  "${GISTOPS_IMAGE_REGISTRY_PREFIX}/gistops-git-mirror:b22a808" \
  gistops run "$@"
}

git_ls_attr() {
  docker run \
  --rm \
  --name "$GISTOPS_CONTAINER_NAME" \
  --workdir "/home/dandens/ws" \
  --volume "$GISTOPS_GIT_ROOT:/home/dandens/ws" \
  "${GISTOPS_IMAGE_REGISTRY_PREFIX}/gistops-git-ls-attr:b22a808" \
  gistops run "$@"
}

jupyter() {
  docker run \
  --rm \
  --name "$GISTOPS_CONTAINER_NAME" \
  --workdir "/home/dandens/ws" \
  --volume "$GISTOPS_GIT_ROOT:/home/dandens/ws" \
  "${GISTOPS_IMAGE_REGISTRY_PREFIX}/gistops-jupyter:b22a808" \
  gistops run "$@"
}

pandoc() {
  docker run \
  --rm \
  --name "$GISTOPS_CONTAINER_NAME" \
  --workdir "/home/dandens/ws" \
  --volume "$GISTOPS_GIT_ROOT:/home/dandens/ws" \
  "${GISTOPS_IMAGE_REGISTRY_PREFIX}/gistops-pandoc:b22a808" \
  gistops run "$@"
}

confluence() {
  docker run \
  --rm \
  --name "$GISTOPS_CONTAINER_NAME" \
  --workdir "/home/dandens/ws" \
  --volume "$GISTOPS_GIT_ROOT:/home/dandens/ws" \
  "${GISTOPS_IMAGE_REGISTRY_PREFIX}/gistops-confluence:b22a808" \
  gistops run "$@"
}

jira() {
  docker run \
  --rm \
  --name "$GISTOPS_CONTAINER_NAME" \
  --workdir "/home/dandens/ws" \
  --volume "$GISTOPS_GIT_ROOT:/home/dandens/ws" \
  "${GISTOPS_IMAGE_REGISTRY_PREFIX}/gistops-jira:b22a808" \
  gistops run "$@"
}

msteams() {
  docker run \
  --rm \
  --name "$GISTOPS_CONTAINER_NAME" \
  --workdir "/home/dandens/ws" \
  --volume "$GISTOPS_GIT_ROOT:/home/dandens/ws" \
  "${GISTOPS_IMAGE_REGISTRY_PREFIX}/gistops-msteams:b22a808" \
  gistops run "$@"
}

############
# Run Jobs #
############
case "$GISTOPS_JOB" in

  "trufflehog")
    trufflehog ${@:3}
    ;;

  "git-mirror")
    git_mirror ${@:3}
    ;;

  "git-ls-attr")
    git_ls_attr ${@:3}
    ;;

  "jupyter")
    jupyter ${@:3}
    ;;

  "pandoc")
    pandoc ${@:3}
    ;;

  "confluence")
    confluence ${@:3}
    ;;

  "jira")
    jira ${@:3}
    ;;

  "msteams")
    msteams ${@:3}
    ;;

  *)
    echo "Unknown job \"$GISTOPS_JOB\"." \
    "Available are trufflehog, git-ls-attr, git-mirror, pandoc, confluence, jira, jupyter, msteams"
    exit 1
    ;;
esac

