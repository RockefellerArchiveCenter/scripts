# extractClipsGetInfo
This script uses ffmpeg to extract clips from MP4 videos whose filenames correspond to ArchivesSpace RefIds, uses the find_by_id endpoint of the ArchivesSpace to retrieve descriptive information, and outputs information to a spreadsheet.

The script requires input from the user into the command line. First, it asks the user for an ArchivesSpace username and password. Then, it asks the user if the RefId is new (always "yes" on the first iteration). Then, it asks for an ArchivesSpace RefId and what number to start with to append to the filename of the clips. Then it asks for when in the video to start the clip, and how long the clip should be. It then creates the clip and puts it in a directory called `Clips`, then gets the video title, dates, AV Number (which is a container indicator), scope and contents note, and collection title and identifier from ArchivesSpace. It then outputs the ArchivesSpace information as well as the RefId, clip filename, when in the video the clip starts, and the clip duration. It then asks the user if they want to start with a new RefId--if the user inputs no, the loop starts with asking for when in the video to start the clip and adds to the number previously specified to append to the clip filename. The user can also quit the script when asked for a new RefId.

## Requirements
*   Python 3
*   ArchivesSnake - https://github.com/archivesspace-labs/ArchivesSnake 

## Installation
Script assumes that it is in the same directory as video files it is creating the clips from and that there is a subdirectory called "Clips" that the extracted clips will be placed in, and that there is a csv file with the filename `inventory.csv` with the following column headings:

Filename | Reference ID | Original Title | Dates | AV Number | Collection | Scope and Contents | Start Time | Duration

Script requires a local configurations file, which should be created in the same directory as the script and named `local_settings.cfg`. A sample file looks like this:

```
    [ArchivesSpace]
    # the base URL of your ArchivesSpace installation
    baseURL:http://localhost:8089
```

