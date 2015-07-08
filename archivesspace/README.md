#archivesspace
These python scripts export data from ArchivesSpace in a variety of formats.

##asExport-ead.py
Creates EAD files from resource records. Export can be scoped to specific records by using an optional argument to match against the resource ID.

##asExport-mets.py
Exports METS files from digital object records.

##asExportIncremental.py
Exports EAD files from published resource records updated since last export, as well as METS records for digital object records associated with those resource records. 
