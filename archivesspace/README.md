#archivesspace
These scripts export data from ArchivesSpace in a variety of formats.

##asExport-ead.py
Creates EAD files from resource records. Export can be scoped to specific records by using an optional argument to match against the resource ID. (Python)

##asExport-mets.py
Exports METS files from digital object records. (Python)

##asPublish.py
Compares resource record IDs against a list, then publishes those which are present and unpublishes those which are not. (Python)
This script requires a local configurations file, which should be created in the same directory as the script and named `local_settings.cfg`. A sample file looks like this:

    [ArchivesSpace]
    # the base URL of your ArchivesSpace installation
    baseURL:http://localhost:8089
    # the id of your repository
    repository:2
    # the username to authenticate with
    user:admin
    # the password for the username above
    password:admin

    [Export]
    # a list of resource IDs to publish
    publishIDs = ["FA001", "FA002","FA003"]
