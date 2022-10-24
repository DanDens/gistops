#!/bin/bash
set -e

####################
# MIRROR FUNCTIONS #
####################
remove_mirror_remote() {
  echo "git remote remove mirror"
  git remote remove mirror
}

add_mirror_remote() {
  local mirror_address=$1 # The address of the mirror repository without the protocol (https)
  local mirror_username=$2 # Username to access the mirror repository
  local mirror_password=$3 # Password matching the username

  # Add mirror repository
  local mirror_url="https://${mirror_address}"
  local exists=$(echo "$(git remote)" | grep 'mirror')
  if [ ! -z "$exists" ]; then
    remove_mirror_remote
  fi
  echo "git remote add mirror \"${mirror_url}\""
  git remote add mirror "https://${mirror_username}:${mirror_password}@$mirror_address"
}

push_to_mirror () {
  # Add mirror repository
  add_mirror_remote $1 $2 $3

  # Push changes to mirror repository
  local mirror_branch=$4 # The branch name of the mirror repository

  echo "git push --set-upstream mirror HEAD:${mirror_branch} --force"
  git push --set-upstream mirror HEAD:${mirror_branch} --force
}


force_delete_merged_branch() {

  local commit_message=$1
  echo "$commit_message"

  branch_name_regex="^[[:space:]]*Merge[[:space:]]branch[[:space:]]'([^']*)'[[:space:]]into[[:space:]]'([^']*)'"
  if ! [[ $commit_message =~ $branch_name_regex ]]; then
    echo "No remote branch to delete as no merge request. All good."
    return # quick return if not an MR
  fi

  local merged_branch="${BASH_REMATCH[1]}"
  local target_branch="${BASH_REMATCH[2]}"
  echo "Detected a merge from $merged_branch into $target_branch. Deleting $merged_branch from mirror ..."

  ticket_naming_convention='^[[:space:]]*[a-zA-Z]{1,}-[0-9]{1,}' # e.g. matching "BSSN-1024...", "con-219-hello"
  if ! [[ $merged_branch =~ $ticket_naming_convention ]]; 
  then 
    echo 'No (conventional) merged branch, such as BSSN-1024..., con-219-hello'
    return # Skip this branch because it is not a conventional branch ...
  fi

  echo "git fetch --all"
  git fetch --all
  echo "git push mirror --delete $merged_branch || true"
  git push mirror --delete $merged_branch || true
}

#####################
# CHECK ENVIRONMENT #
#####################
check_env_exists () {
  env_var_name=$1
  env_var_value="${!env_var_name}"

  # Check Variables exist
  if [ -z "$env_var_value" ]; 
    then
      echo "[ERROR] \"$env_var_name\" not defined but is required to mirror repositories. Please provide a valid env var \"$env_var_name\""
      exit 1
  fi
}

# Ensure Environment Variables are defined and are not empty
check_env_exists 'GITLAB_MIRROR_ADDRESS'
check_env_exists 'GITLAB_MIRROR_USERNAME'
check_env_exists 'GITLAB_MIRROR_PASSWORD'
check_env_exists 'CI_SERVER_HOST'
check_env_exists 'CI_COMMIT_MESSAGE'
check_env_exists 'GITMAGIC_USER_EMAIL'
check_env_exists 'GITMAGIC_USER_NAME'
check_env_exists 'GITMAGIC_ACCESS_TOKEN'

##############
# GIT CONFIG #
##############
# Configure user and email
git config --local user.email "${GITMAGIC_USER_EMAIL}"
git config --local user.name "${GITMAGIC_USER_NAME}"

# Avoid dfwp ssldecrypt issue
echo "git config http.sslVerify false"
git config http.sslVerify false 

###################
# MIRROR BRANCHES #
###################
git_branch=$CI_COMMIT_BRANCH
echo "Current branch is ${git_branch}"

push_to_mirror "$GITLAB_MIRROR_ADDRESS" "$GITLAB_MIRROR_USERNAME" "$GITLAB_MIRROR_PASSWORD" "$CI_COMMIT_BRANCH"

force_delete_merged_branch "$CI_COMMIT_MESSAGE"

