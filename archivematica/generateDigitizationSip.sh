#!/usr/bin/env bash

# input refid
read -p "Enter the ArchivesSpace refid: " refid

#  create directory and subdirectories
mkdir ~/archivematica_test/archivematica_sip_$refid
cd ~/archivematica_test/archivematica_sip_$refid
mkdir logs
mkdir metadata
mkdir objects
mkdir objects/access
mkdir objects/service

# find master files

# copy master files to objects folder


# find service edited files


# copy service edited files to /access folder (and objects folder if concatenated file)


# remove "_se" from files in /access folder


# find master edited files


# copy master edited files to /service folder


# remove "_me" from files in /access folder