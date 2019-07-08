# Archivematica
These scripts are for pre-Archivematica ingest processes.


## Requirements

* Python 3
* generateDigitizationSip.py requires PyPDF2


## generateDigitizationSip.py
This script takes an ArchivesSpace refid and creates an Archivematica-packaged transfer, including master, master edited, and service edited files. The script assumes the following:

*	master files are TIFFs and access files are JPEGs or PDFs
*	filenames include the ArchivesSpace component refids, and are grouped by RefIds

The script requires the following three arguments (order sensitive):

*	The full path to the directory where each RefId directory is
*	The full path to the directory where each SIP should be placed
*	The full path to the a text file containing RefIds (one per line)

The following arguments are optional:

*	Including the -c or --citation flag will remove the first page from master and access files
*	Including the -a or --aspace flag will add an archivesspaceids.csv file to the `/metadata` directory, for use in the ArchivesSpace DIP Upload integration

Example with neither optional flag:
`python3 generateDigitizationSip.py /Users/username/source-location /Users/username/am-transfer-location  /Users/username/refids_list.txt`

Example with both optional flags:
`python3 generateDigitizationSip.py /Users/username/source-location /Users/username/am-transfer-location  /Users/username/refids_list.txt -c -a`


## archivesSpaceCsvDigitization.py
This script takes an ArchivesSpace refid and, if there is already an Archivematica-packaged transfer for digitized documents, creates an archivesspaceids.csv file for the DIP upload integration.

## premisCsvDigitization.py
This script creates a csv file for Archivematica's PREMIS rights csv feature. For each file, the script creates a row with a Copyright rights basis (and an associated act) and a row with a Donor or Policy rights basis (and an associated act). The script requires the following arguments:

```
positional arguments:
  sip_directory         Path to the directory where each SIP is a subdirectory
  refids                Filepath to text file with refids and dates, separated by a tab and one per line.
  {copyrighted,publicdomain,unknown}
  {donor,policy}
```

## generateRfodSip.py

This script requires the following arguments:
```
  source_directory  Path to the directory where the original digital objects
                    (grouped in directories by officers) are.
  sip_directory     Path to the directory where each SIP should be placed.
  officers          Filepath to text file with officers (one per line).
```

And allows for the following optional arguments:

```
-a, --aspace      Option to create the first column of an archivesspaceids.csv file.
  -p, --premis      Option to create a rights.csv file. Assumes creation year is in filename.
```
## startTransfer.py
For each directory in a list, start and then approve an Archivematica transfer.

## fetchDip.py
Downloads, and extracts an Archivematica DIP. Creates derivatives for objects and moves them to flat directory structure. 

