#!/usr/bin/env python

import os, requests, json, sys

# the base URL of your ArchivesSpace installation
baseURL = 'http://localhost:8089'
# the id of your repository
repository = '2'
# the username to authenticate with
user = 'admin'
# the password for the username above
password = 'admin'
# parses arguments, if any. This allows you to pass in an string to match against resource IDs
exportIds = sys.argv[1]
# export destination
destination = '/Users/harnold/Desktop/ead/'

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
        ead = requests.get(baseURL + '/repositories/'+repository+'/resource_descriptions/'+str(id)+'.xml', headers=headers, stream=True)
        if not os.path.exists(destination):
            os.makedirs(destination)
        with open(destination+resourceID+'.xml', 'wb') as f:
            for chunk in ead.iter_content(102400):
                f.write(chunk)
        f.close
print 'Done!'
