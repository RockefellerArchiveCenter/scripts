#!/bin/bash

#takes finding aid number and digital media id as variables to run a virus check over the contents of a directory

get_info () {
#gets FA number and digital media id
  read -p "Please enter the FA number: " FAnumber
  until [ -d /mnt/Disk_Images/FA${FAnumber} ]; do
    read -p "Invalid. Please enter the FA number." FAnumber
  done

  read -p "Please enter the digital media id number: " digital_media
  until [ -d /mnt/Disk_Images/FA${FAnumber}/${digital_media} ]; do
    read -p "Invalid. Please enter the digital media id number." digital_media
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

cd /mnt/Disk_Images/FA${FAnumber}/${digital_media}/

create_outputfile

echo "Scanning for viruses, please wait..."

#run scan, check all files, skip printing OK files
sudo clamscan -r -o --max-filesize=500m --max-scansize=500m /mnt/Disk_Images/FA${FAnumber}/${digital_media}/ >> "/mnt/Disk_Images/FA${FAnumber}/${digital_media}/${digital_media}_scan.txt"

#count the lines that contain "ERROR"
ERROR_COUNT=`grep 'ERROR' /mnt/Disk_Images/FA${FAnumber}/${digital_media}/${digital_media}_scan.txt | wc -l`

#count the lines that contain "FOUND"
FOUND_COUNT=`grep 'FOUND' /mnt/Disk_Images/FA${FAnumber}/${digital_media}/${digital_media}_scan.txt | wc -l`

echo "Scan complete!"
echo "ERRORS: ${ERROR_COUNT} VIRUSES FOUND: ${FOUND_COUNT}"
