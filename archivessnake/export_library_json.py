#!/usr/bin/env python

import os
import json
from asnake.aspace import ASpace
import configparser

config = ConfigParser()
config.read("local_settings.cfg")
aspace = ASpace(
              baseurl=config.get("ArchivesSpace", "baseURL"),
              username=config.get("ArchivesSpace", "user"),
              password=config.get("ArchivesSpace", "password"),
    )
repo = aspace.repositories(2)

###Saves all info (resource, subjects, agents) to GitHub with file name as identifier.json
def save_data(object_type, object):
    path = os.path.join('source_data', object.jsonmodel_type)
    if not os.path.isdir(path):
        os.makedirs(path)
    with open(os.path.join(path, "{}.json".format(object.uri.split('/')[-1])), 'w+') as outfile:
        json.dump(object.json(), outfile, indent=2)
    print(os.path.join(path, "{}.json".format(object.uri.split('/')[-1])))

###get all resources that do not have AC/FA identifier
for object_type in ['resources']:
    for object in getattr(aspace, object_type):
        if not (object.jsonmodel_type == 'resource' and object.id_0.startswith(("FA", "AC.", "AC", "2"))):
            #print(object_type, object)
            save_data(object_type, object)
            ###get associated subject JSON
            for subject in object.subjects:
                #print(subject.json())
                save_data(object_type, subject)
            ##get associated agent JSON
            for agent in object.linked_agents:
                #print(agent.json())
                save_data(object_type, agent)
            ##get associated container JSON
            for instance in object.instances:
                top_container = instance.sub_container.top_container.reify()
                save_data(object_type, top_container)
