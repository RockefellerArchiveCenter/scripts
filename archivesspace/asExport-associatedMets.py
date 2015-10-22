#!/usr/bin/env python

import os
import requests
import json

# the base URL of your ArchivesSpace installation
baseURL = 'http://localhost:8089'
# the id of your repository
repository = 'repository'
# the username to authenticate with
user = 'username'
# the password for the username above
password = 'password'
# export destination
destination = '/path/to/location/'
#list of identifiers for resources whose digital objects you want to export
resource_list = ["test123"]

# authenticates the session
auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session}

# Gets the IDs of all digital objects in the repository
doIds = requests.get(baseURL + '/repositories/'+repository+'/digital_objects?all_ids=true', headers=headers)

# Exports METS for all digital objects
for i in doIds.json():
    try:
        digital_object = (requests.get(baseURL + '/repositories/'+repository+'/digital_objects/' + str(i), headers=headers)).json()
        component_ref = digital_object['linked_instances'][0]['ref']
        component = requests.get(baseURL + component_ref, headers=headers).json()
        resource_ref = component['resource']['ref']
        resource = requests.get(baseURL + resource_ref, headers=headers).json()
        resourceID = resource['id_0']
        if resourceID in resource_list:
            doID = digital_object["digital_object_id"]
            mets = requests.get(baseURL + '/repositories/'+repository+'/digital_objects/mets/'+str(i)+'.xml', headers=headers).text
            if not os.path.exists(os.path.join(destination, doID)):
                os.makedirs(os.path.join(destination, doID))
            f = open(os.path.join(destination, doID, doID)+'.xml', 'w+')
            f.write(mets.encode('utf-8'))
            f.close
            print doID + ' exported to ' + destination
    except:
        print "something went wrong"
