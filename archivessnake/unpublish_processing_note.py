#!/usr/bin/env python

import os
import json
import time
from asnake.aspace import ASpace


def get_resources_notes():
    for object in aspace.resources:
        if object.id_0.startswith('FA'):
            unpublish_notes(object)

def get_ao_notes():
    for object in repo.archival_objects:
        unpublish_notes(object)

def unpublish_notes(object):
    object_json = object.json()
    for idx, note in enumerate(object_json.get('notes')):
        if note.get('type') == 'processinfo':
            note['publish'] = False
            for subnote in note.get('subnotes'):
                subnote['publish'] = False
            object_json['notes'][idx] = note
    updated = aspace.client.post(object.uri, json=object_json)
    if updated.status_code == 200:
        print("{} updated".format(object.uri))
    else:
        print("{} error".format(object.uri))
        pass

if __name__ == '__main__':
    aspace = ASpace()
    repo = aspace.repositories(2)
    start_time = time.time()
    get_ao_notes()
    elapsed_time = time.time() - start_time
    print('Time Elapsed: ' + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))