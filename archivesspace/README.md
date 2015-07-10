#archivesspace
These scripts export data from ArchivesSpace in a variety of formats.

##asExport-ead.py
Creates EAD files from resource records. Export can be scoped to specific records by using an optional argument to match against the resource ID. (Python)

##asExport-mets.py
Exports METS files from digital object records. (Python)

##asExportIncremental.py
Exports EAD files from published resource records updated since last export, as well as METS records for digital object records associated with those resource records. This script is intended to be used with `gitVersion.sh`, which should be located in the same directory. (Python)

##asPublish.py
Compares resource record IDs against a list, then publishes those which are present and unpublishes those which are not. (Python)

##gitVersion.sh
Versions a local git repository and pushes commits to a remote repository. (Bash)
