#!/usr/bin/env python

import os
import json
import time
from asnake.aspace import ASpace


aspace = ASpace(
              baseurl='',
              user='',
              password=''
    )
repo = aspace.repositories(2)
start_time = time.time()


repo = aspace.repositories(2)
start_time = time.time()


def get_resources_notes():
    for object_type in ['resources']:
        for object in getattr(aspace, object_type):
            if (object.jsonmodel_type == 'resource' and object.id_0.startswith(('FA'))):
                unpublish_notes(object)

def get_ao_notes():
    for object in repo.archival_objects:
        unpublish_notes(object)

def unpublish_notes(object):
    object_json = object.json()
    for note in object_json.get('notes'):
        if note["type"] == 'processinfo':
            object_json['publish'] = False
            updated = aspace.client.post(object.uri, json=object_json)
            if updated.status_code == 200:
                print("{} updated".format(object.uri))
            else:
                print(updated.json())

#get_resources_notes()

get_ao_notes()

elapsed_time = time.time() - start_time
print('Time Elapsed: ' + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
