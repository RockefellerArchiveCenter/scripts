#!/bin/bash

# Set seconds variable to 0; needed to calculate imaging duration
SECONDS=0

# Ask user for folder/outputfile
read -p "Enter the digital media ID: " digitalmediaid
read -p "Enter the optical disk type (cdrom, cdrw, dvd, dvdrw): " disktype

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

imagefile="${digitalmediaid}.iso"
echo "Creating ${imagefile}..."
dd if=/dev/$disktype of=$imagefile

get_metadata() {
	# MD5, SHA1, and bytesize to file
	filesystem=$(fsstat $imagefile | awk '/File System Type:/{print $4}')
	md5=$(md5sum $imagefile | awk '{print $1}')
	sha1=$(shasum $imagefile | awk '{print $1}')
	bs=$(ls -l $imagefile |  awk '{print $5}')

	echo "File System Type:" $filesystem
	echo "filesystem:" $filesystem >> $outputfile
	echo "md5:" $md5 >> $outputfile
	echo "sha1:" $sha1 >> $outputfile
	echo "bytesize:" $bs >> $outputfile

	duration=$SECONDS
	echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds" >> $outputfile
	echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."
}

get_metadata

# Other digital forensics information? Filesystem?

