#!/usr/bin/env python

import os
import json
import csv
import time
from asnake.aspace import ASpace


aspace = ASpace(
              baseurl='',
              user='',
              password=''
    )
repo = aspace.repositories(2)
start_time = time.time()


def unpublish_processinfo_resources():
    for object_type in ['resources']:
        print(object_type)
        for object in getattr(aspace, object_type):
            print(object)
            if (object.jsonmodel_type == 'resource' and object.id_0.startswith(("FA"))):
                for note in object.notes:
                    if (note.type == "processinfo"):
                        object_json = object.json()
                        note_json = note.json()
                        note_json["publish"] = False
                        updated = aspace.client.post(object.uri, json=object_json)
                        if updated.status_code == 200:
                            print("Resource {} updated".format(object.uri))
                        else:
                            print(updated.json())

def unpublish_processinfo_ao():
    for object in repo.archival_objects:
            if (object.jsonmodel_type == 'archival_object'):
                for note in object.notes:
                    if (note.type == "processinfo"):
                        object_json = object.json()
                        note_json = note.json()
                        note_json["publish"] = False
                        updated = aspace.client.post(object.uri, json=object_json)
                        if updated.status_code == 200:
                            print("Archival object {} updated".format(object.uri))
                        else:
                            print(updated.json())

#unpublish_processinfo_resources()

unpublish_processinfo_ao()

elapsed_time = time.time() - start_time
print("Time Elapsed: " + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
