#!/bin/bash

#location of local git repository for exported files
REPO=/exports/
#the remote repository to push to
REMOTE=github
#the branch of the remote repository to push to
BRANCH=master

if cd $REPO
  then
  git add .
  git commit -m 'automated commit'
  git push $REMOTE $BRANCH;
fi
