#!/bin/bash
set -e
export DEBIAN_FRONTEND=noninteractive

#####################
# GIT Configuration #
#####################
git config --global credential.helper store
git config --global http.sslverify true

#############
# GIT Alias #
#############
git config --global core.editor "nano"
git config --global alias.lol "log --oneline --graph --decorate --all"
git config --global alias.wcd "whatchanged -p --abbrev-commit --pretty=medium"
git config --global alias.mtn "mergetool --no-prompt"
git config --global alias.sts "status -s" 
git config --global alias.acp '!acp() { git add . && git commit -m "$1" && git push ${2-origin} ; }; acp'

git config --global --list

exit 0 