#!/usr/bin/env python

import os
import requests
import json

# the base URL of your ArchivesSpace installation
baseURL = 'http://your-aspace-url:8089'
# the id of your repository
repository = 'repository-number'
# the username to authenticate with
user = 'username'
# the password for the username above
password = 'password'
# export destination
destination = 'path/to/export/destination'

# authenticates the session
auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session}

# Gets the IDs of all resources in the repository
doIds = requests.get(baseURL + '/repositories/'+repository+'/digital_objects?all_ids=true', headers=headers)

# Exports EAD for all resources whose IDs contain 'FA'
for id in doIds.json():
    digital_object = (requests.get(baseURL + '/repositories/'+repository+'/digital_objects/' + str(id), headers=headers)).json()
    doID = digital_object["digital_object_id"]
    mets = requests.get(baseURL + '/repositories/'+repository+'/digital_objects/mets/'+str(id)+'.xml', headers=headers).text
        
    if not os.path.exists(destination):
        os.makedirs(destination)
    f = open(destination+doID+'.xml', 'w')
    f.write(mets.encode('utf-8'))
    f.close
    print doID + ' exported to ' + destination