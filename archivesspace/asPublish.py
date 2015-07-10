#!/usr/bin/env python

import os
import requests
import json
import sys

# the base URL of your ArchivesSpace installation
baseURL = 'http://as-url:8089'
# the id of your repository
repository = '2'
# the username to authenticate with
user = 'user'
# the password for the username above
password = 'password'
# a list of resource IDs to publish
publishIDs = ['FA001', 'FA002']

# authenticates the session
auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session}

# Gets the IDs of all resources in the repository
print 'Getting a list of resources'
resourceIds = requests.get(baseURL + '/repositories/'+repository+'/resources?all_ids=true', headers=headers)

for id in resourceIds.json():
    resource = (requests.get(baseURL + '/repositories/'+repository+'/resources/' + str(id), headers=headers)).json()
    resourceID = resource["id_0"]
    # Publish the resource record if it's in the publish list...
    if resourceID in publishIDs:
        resource["publish"] = True
        updated = requests.post(baseURL + '/repositories/'+repository+'/resources/' + str(id), headers=headers, data=json.dumps(resource))
        status = updated.json()
        if status["status"] == 'Updated':
            print resourceID + ' published'
        else:
            print status["warnings"]
    # ...otherwise unpublish the resource record
    else:
        resource["publish"] = False
        updated = requests.post(baseURL + '/repositories/'+repository+'/resources/' + str(id), headers=headers, data=json.dumps(resource))
        status = updated.json()
        if status["status"] == 'Updated':
            print resourceID + ' unpublished'
        else:
            print status["warnings"]
print 'Done!'
