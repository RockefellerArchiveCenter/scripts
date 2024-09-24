# Removing Ingested Digital Objects 

Sometimes digital objects get ingested by mistake, or get attached to the incorrect archival object. In these cases it is necessary to remove a number of different pieces of data:
    - The AIP in Archivematica
    - Packages stored in Fedora
    - The digital object reference in ArchivesSpace

If digital objects are being reingested, you will also need to do the following to ensure they can be processed:
    - Remove the objects' refids from the `processed_list.txt` file in the dart_runner pipeline
    - Remove the database objects in Zorya matching the objects' refids
    - Invalidate the CloudFront cache for the objects manifests and PDFs.


## Removing data from Archivematica, ArchivesSpace and Fedora

The `delete_digital_objects_and_aips.py` script deletes digital objects from ArchivesSpace, creates delete requests for AIPs from Archivematica, and removes files from Fedora. It is necessary to manually approve AIP deletion from Archivematica.

This script needs to be passed a filepath for a CSV file containing a list of ArchivesSpace URIs of objects to be processed.


## Supporting reingest
The `remove_refids` script removes the refids contained in a given filepath from the `processed_list.txt` file in the dart_runner pipeline. 

The same list of refids can be used to remove database objects from Zorya by entering the Django shell for the application and then executing the following commands:
```
refids = ["c3d7df0e36cf4ff7b0e230014799d5b1", ... ]
from package_bag.models import Bag
for r in refids:
    Bag.objects.get(original_bag_name__contains=r).delete()
```

The CloudFront cache for IIIF Assets will also need to be invalidated, which can be done from the AWS console.

