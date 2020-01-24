#!/usr/bin/env python

# Gets all objects from ArchivesSpace. Takes a very long time to run

import os
import json
from asnake.aspace import ASpace
aspace = ASpace(
              baseurl='http://192.168.50.4:8089',
              user='admin',
              password='admin'
              )
repo = aspace.repositories(2)


def save_data(object_type, object):
    path = os.path.join('source_data', object.jsonmodel_type) if (object_type == 'agents') else os.path.join('source_data', object_type)
    if not os.path.isdir(path):
        os.makedirs(path)
    with open(os.path.join(path, "{}.json".format(object.uri.split('/')[-1])), 'w+') as outfile:
        json.dump(object.json(), outfile, indent=2)
    print(os.path.join(path, "{}.json".format(object.uri.split('/')[-1])))

for object_type in ['resources', 'archival_objects']:
    for object in getattr(aspace, object_type):
        if not (object.jsonmodel_type == 'resource' and object.id_0.startswith('LI')):
            save_data(object_type, object)

for object_type in ['agents', 'subjects']:
    for object in getattr(aspace, object_type):
        save_data(object_type, object)
