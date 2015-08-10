#archivesspace
These scripts export data from ArchivesSpace in a variety of formats.

##asExport-ead.py
Creates EAD files from resource records. Export can be scoped to specific records by using an optional argument to match against the resource ID. (Python)

##asExport-mets.py
Exports METS files from digital object records. (Python)

##asPublish.py
Compares resource record IDs against a list, then publishes those which are present and unpublishes those which are not. (Python)