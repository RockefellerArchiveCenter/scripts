#!/usr/bin/env python

import os
import requests
import json
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('local_settings.cfg')
dictionary = {'baseURL': config.get('ArchivesSpace', 'baseURL'), 'repository':config.get('ArchivesSpace', 'repository'), 'user': config.get('ArchivesSpace', 'user'), 'password': config.get('ArchivesSpace', 'password'), 'destination': config.get('Destinations', 'METSdestination')}

# authenticates the session
auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session}

# Gets the IDs of all digital objects in the repository
doIds = requests.get(baseURL + '/repositories/'+repository+'/digital_objects?all_ids=true', headers=headers)

# Exports METS for all digital objects
for id in doIds.json():
    digital_object = (requests.get(baseURL + '/repositories/'+repository+'/digital_objects/' + str(id), headers=headers)).json()
    doID = digital_object["digital_object_id"]
    mets = requests.get(baseURL + '/repositories/'+repository+'/digital_objects/mets/'+str(id)+'.xml', headers=headers).text

    if not os.path.exists(os.path.join(destination, doID)):
        os.makedirs(os.path.join(destination, doID))
    f = open(os.path.join(destination, doID, doID)+'.xml', 'w+')
    f.write(mets.encode('utf-8'))
    f.close
    print doID + ' exported to ' + destination
