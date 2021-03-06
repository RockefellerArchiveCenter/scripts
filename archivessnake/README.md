# archivessnake

These scripts use ArchivesSnake to export data from ArchivesSpace in a variety of formats.

## Requirements

*   Python 3
*   ArchivesSnake - https://github.com/archivesspace-labs/ArchivesSnake
*   ffmpeg (for extractClipsGetInfo)
*   FuzzyWuzzy - https://github.com/seatgeek/fuzzywuzzy (for edit_notes)
*   requests - https://requests.readthedocs.io/en/master/ (for edit_notes)

## Installation

These scripts require a local configurations file, which should be created in the same directory as the script and named `local_settings.cfg`. A sample file looks like this:

```
    [ArchivesSpace]
    # the base URL of your ArchivesSpace installation
    baseURL:http://localhost:8089
    username:admin
    password:admin
```

## extractClipsGetInfo

This script uses ffmpeg to extract clips from MP4 videos whose filenames correspond to ArchivesSpace RefIds, uses the find_by_id endpoint of the ArchivesSpace API to retrieve descriptive information, and outputs information to a spreadsheet.

The script requires input from the user into the command line. First, it asks the user for an ArchivesSpace username and password. Then, it asks the user if the RefId is new (always "yes" on the first iteration). Then, it asks for an ArchivesSpace RefId and what number to start with to append to the filename of the clips. Then it asks for when in the video to start the clip, and how long the clip should be. It then creates the clip and puts it in a directory called `Clips`, then gets the video title, dates, AV Number (which is a container indicator), scope and contents note, and collection title and identifier from ArchivesSpace. It then outputs the ArchivesSpace information as well as the RefId, clip filename, when in the video the clip starts, and the clip duration. It then asks the user if they want to start with a new RefId--if the user inputs no, the loop starts with asking for when in the video to start the clip and adds to the number previously specified to append to the clip filename. The user can also quit the script when asked for a new RefId.

Script assumes that it is in the same directory as video files it is creating the clips from and that there is a subdirectory called "Clips" that the extracted clips will be placed in, and that there is a csv file with the filename `inventory.csv` with the following column headings:

Filename | Reference ID | Original Title | Dates | AV Number | Collection | Scope and Contents | Start Time | Duration


## findByRefid

This script takes an input of a textfile (`refids.txt`) where each line is an ArchivesSpace refid, uses the find_by_id endpoint of the ArchivesSpace API to retrieve descriptive information, and outputs information to a spreadsheet. The spreadsheet contains the following columns:

* RefId - RefId of the archival object
* Title - title of the archival object, or its parent title if no title exists
* Component Dates - dates of the archival object, structured as YYYY-YYYY where possible, or left blank if "n.d." or "undated"
* Component Level - level of the archival object
* Component Access Restricton - access restriction of the archival object
* Ancestor - first (non-resource) parent of the archival object, or second if archival object did not have a title
* Ancestor Level - level of the parent of the archival object
* Ancestor Dates - dates of the parent of the archival object, structured as YYYY-YYYY where possible, or left blank if "n.d." or "undated"
* Ancestor Access Restriction - access restriction of the parent of the archival object
* Parent Resource - parent resource of the archival object
* Resource Dates - dates of the parent resource, structured as YYYY-YYYY where possible, or left blank if "n.d." or "undated"
* Resource Creator(s) - agents linked to the parent resource with the role "creator"
* Resource Access Restriction - conditions governing access note of the parent resource
* Resource Use Restriction - conditions governing use note of the parent resource


## archival_objects_by_collection

Exports information about all archival objects in a resource tree to a CSV file. Has one required argument, which is the ArchivesSpace identifier for the resource record whose tree will be walked. 

## edit_notes

A script to modify or delete specified notes within an ArchivesSpace resource record. This script is useful if there are a number of the same notes within a finding aid that need to be changed or deleted simultaneously. When running the script, the user enters note type (ex. bioghist for a biographical/historical note), the action type (modify or delete), resource ID (must be an integer), the original content of the note you want to change or delete, the level of a note within a finding aid hierarchy that the user wants to change (ex. file), and the new note content if modifying existing notes (not required if deleting). A log of the changes are printed to the console and the instance information for changed objects are recorded in a spreadsheet.  

The script utilizes argparse, a python module that allows users to write commands directly in the command line that the script can easily parse. If a command is written incorrectly, the argparse module will also provide help messages. For the edit_notes script, you need to provide: 
 
 - note type: "bioghist", "accessrestrict", "odd", "abstract", "arrangement", "userestrict", "fileplan", "acqinfo", "langmaterial", "physdesc", "prefercite", "processinfo", "separatedmaterial" or "relatedmaterial"
 
 - action choice: "modify" or "delete"
 
 - resource identifier: The number found within the URL of a record (ex. 11413)
 
 - search string: Should be in quotes. The string to be matched against the resource record notes (in other words the note content you want to change or delete).
 
 - level: "collection", "file", "series"
 
 - replace string (optional, only necessary if modifying notes): Should be in quotes. The new note content to replace the old note content.
 
 To run the script, a sample command might look like this: python3 edit_notes.py bioghist modify 11413 "the current note content" file -r "new note content"
 
 The script also uses fuzzywuzzy, a Python library used for string matching, to ensure that no note content is changed unintentionally. Currently, the ratio between the user input and the note contents within a resource is 97%. This can be changed by editing the CONFIDENCE_RATIO.
