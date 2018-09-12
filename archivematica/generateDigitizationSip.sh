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
		# check that access directory is not empty
	done
fi
if [[ " ${array[*]} " == *".pdf"* ]]; then
    echo "access copies are pdfs"
	for i in ${array[@]}
	do
		echo $i
		cp $i ~/archivematica_test/archivematica_sip_$refid/objects/access/${i/_se/}
		cp $i ~/archivematica_test/archivematica_sip_$refid/objects/${i/_se/}
		# check number of files in access directory equal number of files in objects directory
	done
fi

# find master edited files and copy master edited files to /service folder
cd ~/archivematica_test/Master\ Edited
array=(`find ${refid}*`)
for i in ${array[@]}
do
	echo $i
	cp $i ~/archivematica_test/archivematica_sip_$refid/objects/service/${i/_me/}
	# check number of files in service directory equal number of files in objects directory
	
done

master_filelist_count=(`ls ~/archivematica_test/archivematica_sip_$refid/objects/ | wc -l`)
echo "There are ${master_filelist_count} files and directories in the /objects directory"

service_filelist_count=(`ls ~/archivematica_test/archivematica_sip_$refid/objects/service/ | wc -l`)
echo "There are ${service_filelist_count} files and directories in the /objects/service directory"


access_filelist_count=(`ls ~/archivematica_test/archivematica_sip_$refid/objects/access/ | wc -l`)
echo "There are ${access_filelist_count} files and directories in the /objects/access directory"