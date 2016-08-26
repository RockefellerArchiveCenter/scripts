#archivesspace
These scripts export data from ArchivesSpace in a variety of formats.

##Requirements
*   Python
*   Requests module
*   ConfigParser

## Installation

Download [Python](https://www.python.org/downloads/) (must be 2.7 or higher).

If using Python 3 or higher, note that URLLib2 and ConfigParser have been renamed. Please see [here](http://stackoverflow.com/questions/16597865/is-there-a-library-for-urllib2-for-python-which-we-can-download) for support for URLLib2 and [here](http://stackoverflow.com/questions/14087598/python-3-3-importerror-no-module-named-configparser) for support for ConfigParser.

For further instructions on including Python in your PATH variable see [here](https://docs.python.org/2/using/windows.html).
For instructions on installing Python on Linux, see [here](http://docs.python-guide.org/en/latest/starting/install/linux/).

For further instructions on installing the Requests module through easy_install, see [here](http://stackoverflow.com/questions/17309288/importerror-no-module-named-requests).

Save `asExport-associatedMets.py`, `asExport-ead.py`, `asExport-mets.py`, and `asPublish.py` to your Python installation directory.

Some of these scripts require a local configurations file, which should be created in the same directory as the script and named `local_settings.cfg`. A sample file looks like this:

    [ArchivesSpace]
    # the base URL of your ArchivesSpace installation
    baseURL:http://localhost:8089
    # the id of your repository
    repository:2
    # the username to authenticate with
    user:admin
    # the password for the username above
    password:admin

    [Logging]
    filename = log.txt
    format = %(asctime)s %(name)s %(levelname)s %(message)s
    datefmt = %a, %d %b %Y %H:%M:%S
    level = DEBUG

    [Export]
    # a list of resource IDs to publish
    publishIDs = ["FA001", "FA002","FA003"]

You can use the `config_settings.py` file found [here] (https://github.com/RockefellerArchiveCenter/templates/blob/master/config_setup.py) to automatically create a `local_settings.cfg` file.

##Usage
In the console or terminal, navigate to the directory containing the script you want and execute the script.
*   On Windows this will be something like `python asExport-ead.py`
*   On Mac or Linux systems you can simply type `./asExport-ead.py`

##asExport-ead.py
Creates EAD files from resource records. Export can be scoped to specific records by using an optional argument to match against the resource ID. (Python)

##asExport-mets.py
Exports METS files from digital object records. (Python)

##asPublish.py
Compares resource record IDs against a list, then publishes those which are present and unpublishes those which are not. (Python)

##asCSV-accessions.py
Exports accessions data in a comma-separated file format. (Python)
