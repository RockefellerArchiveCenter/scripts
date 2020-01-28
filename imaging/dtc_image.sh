#!/bin/bash

# Set seconds variable to 0; needed to calculate imaging duration
SECONDS=0

# Ask user for folder/outputfile
read -p "Enter the digital media ID: " digitalmediaid

create_folder() {
	mkdir $digitalmediaid
	cd $digitalmediaid
	current_directory=$(pwd)
	echo "In directory $current_directory"
}

create_outputfile() {
	outputfile="${digitalmediaid}.txt"
	echo "Creating ${outputfile}..."

	# Log time/date/system of imaging into to file
	imaging_date=$(date +"%Y-%m-%d")
	echo "Today's date: $imaging_date"
	echo $imaging_date >> $outputfile
}

create_folder

create_outputfile

# Ask user for image type
read -p "Enter the floppy disk type. MFM is 4: " imagetype

# Create disk image
imagefile="${digitalmediaid}.img"
echo "Creating ${imagefile}..."
#./dtc -f$imagename -i$imagetype  

get_metadata (){
	# MD5, SHA1, and bytesize to file
	filesystem=$(fsstat $imagefile | awk '/File System Type:/{print $4}')
	md5=$(md5 $imagefile | awk '{print $4}')
	sha1=$(shasum $imagefile | awk '{print $1}')
	bs=$(ls -l $imagefile |  awk '{print $5}')

	#echo fls -r -l 2012_069_DM0000000006.img | awk -F '\t' '{print $2, $3, $3, $6, $7}' > ${digitalmediaid}_filelist.txt
	echo "File System Type:" $filesystem
	echo "filesystem:" $filesystem >> $outputfile
	echo "md5:" $md5 >> $outputfile
	echo "sha1:" $sha1 >> $outputfile
	echo "bytesize:" $bs >> $outputfile

	duration=$SECONDS
	echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds" >> $outputfile
	echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."}

get_metadata

# Other digital forensics information? Filesystem?
