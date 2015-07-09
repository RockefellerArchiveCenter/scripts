#!/bin/bash

#location of local git repository for exported files
REPO=/Users/harnold/Desktop/export/
#the remote repository to push to
REMOTE=github
#the branch of the remote repository to push to
BRANCH=master

cd $REPO;

git add .
git commit -m 'automated commit'
git push $REMOTE $BRANCH;
