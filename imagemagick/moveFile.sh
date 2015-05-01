#!/bin/bash
TMP=/var/tmp
WWW=/var/www
# Move files from tmp directory to www
cd $TMP;
if [ "$(ls -A $TMP)" ]; then
    for file in `ls *.*`; do
        sudo mv $file $WWW
    done
    echo 'All files moved'
    cd $WWW
    for file in `ls *.*`; do
        sudo chmod 664 $file
    done
    else
    echo 'No files to move'
fi