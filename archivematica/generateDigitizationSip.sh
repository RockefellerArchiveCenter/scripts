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
mkdir objects/tiffs

# copy service edited files to /access folder (and objects folder if concatenated file)


# copy master edited files to objects folder


# copy master files to /tiffs folder