#!/usr/bin/env bash

REFID_FILEPATH=$1

if [ $# -eq 0 ]
  then
    echo "Please pass the name of a file containg refids as the first argument."
    exit
fi

while read p; do
  echo "$p"
  sed -e s/$p//g -i /data/dart_runner_files/processed_list.txt
done <$REFID_FILEPATH