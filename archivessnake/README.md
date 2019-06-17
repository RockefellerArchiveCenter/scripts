# archivessnake

These scripts use ArchivesSnake to export data from ArchivesSpace in a variety of formats.

## Requirements

*   Python 3
*   ArchivesSnake - https://github.com/archivesspace-labs/ArchivesSnake
*   ffmpeg (for extractClipsGetInfo)

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
