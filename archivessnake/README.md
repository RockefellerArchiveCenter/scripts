# archivessnake

These scripts use ArchivesSnake to export data from ArchivesSpace in a variety of formats.

## Requirements

*   Python 3
*   ArchivesSnake - https://github.com/archivesspace-labs/ArchivesSnake
*   ffmpeg (for extractClipsGetInfo)
*   FuzzyWuzzy - https://github.com/seatgeek/fuzzywuzzy (for edit_notes)
*   requests - https://requests.readthedocs.io/en/master/ (for edit_notes)

## Installation

These scripts require a local ArchivesSnake configuration file. See the 
[official documentation](https://github.com/archivesspace-labs/ArchivesSnake/#configuration) 
for the location and format of this file.

The script `create_daos.py` requires a local configuration file located 
in the same directory as the script and named `local_settings.cfg`. It
 must contain an `Archivematica` section, which looks like this:

```
[Archivematica]
# the base URL of the Archivematica storage service
ss_baseurl:http://localhost:8000
api_key:nc9u4zby5aj4pjmdaaq59u1ixhtdexwl4ljef7o6
username:admin
```