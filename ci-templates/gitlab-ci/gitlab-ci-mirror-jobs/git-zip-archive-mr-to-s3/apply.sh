#!/bin/bash
set -e

####################
# MIRROR FUNCTIONS #
####################
archive_to_s3 () {
  local s3_archieved_ref_uri="$1" # The address of the s3 access point in from s3://...
  local aws_region="$2"
  local aws_access_key_id="$3" # S3_AWS_ACCESS_KEY_ID
  local aws_secret_access_key="$4" # S3_AWS_SECRET_ACCESS_KEY
  local reference="$5" # e.g. HEAD or 65ccf3

  # 1. git archive 
  archieved_ref_zip='archieved.ref.zip'
  echo 'git archive --format=zip -o "'"$archieved_ref_zip"'" "'"$reference"'"'
  git archive --format=zip -o "$archieved_ref_zip" "$reference"

  # 2. zip conventional.semver.json
  conventional_semver_json='conventional.semver.json'
  echo -n '{"branch":"'"${CI_MERGE_REQUEST_TARGET_BRANCH_NAME}"'","target":"","id":"mr'"${CI_MERGE_REQUEST_IID}"'","message":"'"$(echo -n ${CI_MERGE_REQUEST_TITLE} | sed 's/\"//g')"'","version":"mr'"${CI_MERGE_REQUEST_IID}"'","type":"candidate"}' > "$conventional_semver_json"
  echo "$(cat $conventional_semver_json)"

  echo 'zip -j "'"$archieved_ref_zip"'" "'"$conventional_semver_json"'"'
  zip -j "$archieved_ref_zip" "$conventional_semver_json"

  # 3. upload to s3
  echo 'export AWS_ACCESS_KEY_ID="'"$aws_access_key_id"'"' 
  echo 'export AWS_SECRET_ACCESS_KEY="..."' 
  echo 'export AWS_DEFAULT_REGION="'"$aws_region"'"' 
  echo 'aws s3 --region "'"$aws_region"'" cp "'"$archieved_ref_zip"'" "'"$s3_archieved_ref_uri"'"' 
  export AWS_ACCESS_KEY_ID="$aws_access_key_id" 
  export AWS_SECRET_ACCESS_KEY="$aws_secret_access_key"
  export AWS_DEFAULT_REGION="$aws_region"
  aws s3 --region "$aws_region" cp "$archieved_ref_zip" "$s3_archieved_ref_uri"
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
check_env_exists 'GITMAGIC_USER_EMAIL'
check_env_exists 'GITMAGIC_USER_NAME'
check_env_exists 'S3_ARCHIEVED_REF_URI'
check_env_exists 'S3_AWS_ACCESS_KEY_ID'
check_env_exists 'S3_AWS_SECRET_ACCESS_KEY'
check_env_exists 'S3_AWS_REGION'
check_env_exists 'CI_MERGE_REQUEST_IID'
check_env_exists 'CI_MERGE_REQUEST_TITLE'
check_env_exists 'CI_MERGE_REQUEST_TARGET_BRANCH_NAME'

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
reference='HEAD'

archive_to_s3 "$S3_ARCHIEVED_REF_URI" "$S3_AWS_REGION" "$S3_AWS_ACCESS_KEY_ID" "$S3_AWS_SECRET_ACCESS_KEY" "$reference"
