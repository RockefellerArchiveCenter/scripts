# X Drive Cleanup

These files were designed to support making unrestricted digital content
from the X Drive available in DIMES.

## What's Here
- `create_inventory.py` creates an inventory of packages currently stored on the X drive,
  fetching additional data from ArchivesSpace to support rights assessment.
- `process_package.py` processes a single package and uploads it to the digitized image
  pipeline upload bucket. This script is designed to be run in the context of a Docker
  container (see associated `Dockerfile`, `requirements.txt` and `.env` files).