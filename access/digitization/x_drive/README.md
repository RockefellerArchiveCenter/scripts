# X Drive Cleanup

These files were designed to support making unrestricted digital content
from the X Drive available in DIMES.

## What's Here
- `create_inventory.py` creates an inventory of packages currently stored on the X drive,
  fetching additional data from ArchivesSpace to support rights assessment.
- `process_packages.py` processes packages listed in a spreadsheet. Valid packages are uploaded to 
  S3, and invalid or restricted packages are moved to separate directories.
- `validate_packages.py` validates packages listed in a spreadsheet. Validation errors are printed
  to the console.