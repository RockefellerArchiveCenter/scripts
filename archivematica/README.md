# Archivematica
These scripts are for pre-Archivematica ingest processes.


## Requirements
Python scripts use Python 3. To run bash scripts on a Windows machine, use a Unix-like environment like Cygwin.



## generateDigitizationSip.sh
This script takes an ArchivesSpace refid and creates an Archivematica-packaged transfer, including master, master edited, and service edited files. The script assumes the following:

*	master files are TIFFs, and service edited (i.e., access) files are JPEGs or PDFs
*	filenames include the ArchivesSpace component refid
*	master files are in directory "Master," master edited files are in directory "Master Edited," and serviced edited files are in directory "Service Edited"

The output should look like either of the following (depending on access format):

```
/archivematica_sip_examplerefid
	/logs
	/metadata
	/objects
		examplerefid_001_me.tif
		examplerefid_002_me.tif
		examplerefid_003_me.tif
		examplerefid_se.pdf
		/access
			examplerefid_se.pdf
		/service
			examplerefid_001.tif
			examplerefid_002.tif
			examplerefid_003.tif
```

```
/archivematica_sip_examplerefid
	/logs
	/metadata
	/objects
		examplerefid_001.tif
		examplerefid_002.tif
		examplerefid_003.tif
		/access
			examplerefid_001.jpg
			examplerefid_002.jpg
			examplerefid_003.jpg
		/service
			examplerefid_001.tif
			examplerefid_002.tif
			examplerefid_003.tif
```
## archivesSpaceCsvDigitization.py
This script takes an ArchivesSpace refid and, if there is already an Archivematica-packaged transfer for digitized documents, creates an archivesspaceids.csv file for the DIP upload integration.

## premisCsvDigitization.py
This script creates a csv file for Archivematica's PREMIS rights csv feature. For each file, the script creates a row with a Copyright rights basis (and an associated act) and a row with a Donor rights basis (and an associated act).
