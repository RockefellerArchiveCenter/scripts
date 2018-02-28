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

# find master files and copy master files to objects folder
cd ~/archivematica_test/Master
array=(`find ${refid}*`)
for i in ${array[@]}
do
	echo $i
	cp $i ~/archivematica_test/archivematica_sip_$refid/objects
done


# find service edited files and copy service edited files to /access folder (and objects folder if concatenated file)
cd ~/archivematica_test/Service\ Edited
array=(`find ${refid}*`)
if [[ " ${array[*]} " == *".jpg"* ]]; then
    echo "access copies are jpgs"
	for i in ${array[@]}
	do
		echo $i
		cp $i ~/archivematica_test/archivematica_sip_$refid/objects/access/${i/_se/}
	done
fi
if [[ " ${array[*]} " == *".pdf"* ]]; then
    echo "access copies are pdfs"
	for i in ${array[@]}
	do
		echo $i
		cp $i ~/archivematica_test/archivematica_sip_$refid/objects/access
		cp $i ~/archivematica_test/archivematica_sip_$refid/objects/${i/_se/}
	done
fi


# find master edited files and copy master edited files to /service folder
cd ~/archivematica_test/Master\ Edited
array=(`find ${refid}*`)
for i in ${array[@]}
do
	echo $i
	cp $i ~/archivematica_test/archivematica_sip_$refid/objects/service/${i/_me/}
done
