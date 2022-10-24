#!/bin/bash
set -e

####################
# MIRROR FUNCTIONS #
####################
add_mirror_remote() {
  local mirror_address=$1 # The address of the mirror repository without the protocol (https)
  local mirror_username=$2 # Username to access the mirror repository
  local mirror_password=$3 # Password matching the username

  # Add mirror repository
  local mirror_url="https://${mirror_address}"
  local exists=$(echo "$(git remote)" | grep 'mirror')
  if [ ! -z "$exists" ]; then
    echo "git remote remove mirror"
    git remote remove mirror
  fi
  echo "git remote add mirror \"${mirror_url}\""
  git remote add mirror "https://${mirror_username}:${mirror_password}@$mirror_address"
}

force_checkout_mirror_branch () {
  # Pull changes from mirror repository
  local branch_name=$1 
  # local mirror_branch="mirror/$branch_name"

  echo "git checkout origin/$CI_COMMIT_BRANCH"
  git checkout origin/$CI_COMMIT_BRANCH

  # git fetch only on depth=1
  echo "git fetch -k mirror $branch_name"
  git fetch -k mirror $branch_name
  
  # Delete a local branch with that name if it exsits
  echo "git branch -D ${branch_name} &>/dev/null || true"
  git branch -D ${branch_name} &>/dev/null || true

  echo "git checkout -b ${branch_name} mirror/$branch_name"
  git checkout -b ${branch_name} mirror/$branch_name
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

echo "Checkout branch is origin/$CI_COMMIT_BRANCH"

###############
# ADD REMOTES #
###############
# Push changes of this protected branch to the gitlab server
this_url="https://${CI_SERVER_HOST}/${CI_PROJECT_PATH}"
if echo "$(git remote)" | grep 'this'; then
  git remote remove this
fi

echo "git remote add this $this_url"
git remote add this "https://oauth2:${GITMAGIC_ACCESS_TOKEN}@${CI_SERVER_HOST}/${CI_PROJECT_PATH}"

# Add mirror repository
add_mirror_remote $GITLAB_MIRROR_ADDRESS $GITLAB_MIRROR_USERNAME $GITLAB_MIRROR_PASSWORD


###################
# MIRROR BRANCHES #
###################
# get remote branches
echo "git ls-remote --heads mirror | grep -oE 'refs/heads/(.*)$' | sed 's;refs/heads/;;g'"
all_mirror_branches=$(git ls-remote --heads mirror | grep -oE 'refs/heads/(.*)$' | sed 's;refs/heads/;;g')

# For each branch in remote mirror
for branch_name in $all_mirror_branches; 
do
  ticket_naming_convention='^[[:space:]]*[a-zA-Z]{1,}-[0-9]{1,}' # e.g. matching "BSSN-1024...", "con-219-hello"
  if ! [[ $branch_name =~ $ticket_naming_convention ]]; 
  then # Skip this branch ...
    echo "$branch_name does not match $ticket_naming_convention. Skipping ..."
    continue 
  fi

  force_checkout_mirror_branch $branch_name

  # Overwrite branch content on this Gitlab
  echo "git push --set-upstream this HEAD:${branch_name} --force"
  git push --set-upstream this HEAD:${branch_name} --force

done
