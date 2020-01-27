#!/bin/bash

#takes finding aid number, digital media id, and extension as variables to mount a disk image and run a virus check


#checks to see if disk is mounted or not
check_mount () {
if mountpoint -q /media/cdrom ; then
	echo "Mounted"
else
	echo "Not Mounted"
fi
}

get_info () {
#gets FA number, digital media id, and type of image
  read -p "Please enter the FA number: " FAnumber
  until [ -d /mnt/Disk_Images/FA${FAnumber} ]; do
    read -p "Invalid. Please enter the FA number." FAnumber
  done

  read -p "Please enter the digital media id number: " digital_media
  until [ -d /mnt/Disk_Images/FA${FAnumber} ]; do
    read -p "Invalid. Please enter the digital media id number." digital_media
  done

  read -p  "Please enter the file extension, exclude the preceding period: " extension
	until [ -e /mnt/Disk_Images/FA${FAnumber}/${digital_media}/${digital_media}.${extension} ]; do
		read -p "Invalid. Please enter the file extension, excluding the preceding period " extension
	done
}

create_outputfile () {
	cd /mnt/Disk_Images/FA${FAnumber}/${digital_media}/
	outputfile="${digital_media}_scan.txt"
	echo "Creating ${outputfile}..."
	scan_date=$(date +"%Y-%m-%d")
	echo $scan_date >> $outputfile
}

get_info

check_mount

mount -o ro,loop /mnt/Disk_Images/FA${FAnumber}/${digital_media}/${digital_media}.${extension} /media/cdrom

check_mount

create_outputfile

echo "Scanning for viruses, please wait..."

#run scan, check all files, skip printing OK files
sudo clamscan -r -o --max-filesize=500m --max-scansize=500m /media/cdrom >> "/mnt/Disk_Images/FA${FAnumber}/${digital_media}/${digital_media}_scan.txt"

#count the lines that contain "ERROR"
ERROR_COUNT=`grep 'ERROR' /mnt/Disk_Images/FA${FAnumber}/${digital_media}/${digital_media}_scan.txt | wc -l`

#count the lines that contain "FOUND"
FOUND_COUNT=`grep 'FOUND' /mnt/Disk_Images/FA${FAnumber}/${digital_media}/${digital_media}_scan.txt | wc -l`

echo "Scan complete!"
echo "ERRORS: ${ERROR_COUNT} VIRUSES FOUND: ${FOUND_COUNT}"

sudo umount /media/cdrom

check_mount
