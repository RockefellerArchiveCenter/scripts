#!/bin/bash
REPO=/Users/harnold/Desktop/test/
cd $REPO;

git add .
git commit -m 'automated commit'
git push github master

echo 'New commit pushed to GitHub'
