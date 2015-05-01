#!/usr/bin/env python

import os
import requests
import json
import sys

# the base URL of your ArchivesSpace installation
baseURL = 'http://your-aspace-url:8089'
# the id of your repository
repository = 'repository-number'
# the username to authenticate with
user = 'username'
# the password for the username above
password = 'password'
# parses arguments, if any. This allows you to pass in an string to match against resource IDs
exportIds = sys.argv[1]
# export destination
destination = 'path/to/export/destination'

# authenticates the session
auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session}

# Gets the IDs of all resources in the repository
print 'Getting a list of resources'
resourceIds = requests.get(baseURL + '/repositories/'+repository+'/resources?all_ids=true', headers=headers)

# Exports EAD for all resources whose IDs contain argument
for id in resourceIds.json():
    resource = (requests.get(baseURL + '/repositories/'+repository+'/resources/' + str(id), headers=headers)).json()
    resourceID = resource["id_0"]
    if exportIds in resourceID:
        print 'Exporting ' + resourceID
        ead = requests.get(baseURL + '/repositories/'+repository+'/resource_descriptions/'+str(id)+'.xml', headers=headers).text

        if not os.path.exists(destination):
            os.makedirs(destination)
        f = open(destination+resourceID+'.xml', 'w')
        f.write(ead.encode('utf-8'))
        f.close
        print resourceID + ' exported to ' + destination
print 'Done!'