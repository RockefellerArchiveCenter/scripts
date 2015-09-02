#!/usr/bin/env python

import os, requests, json, sys, ConfigParser

config = ConfigParser.ConfigParser()
config.read('local_settings.cfg')

dictionary = {'baseURL': config.get('ArchivesSpace', 'baseURL'), 'repository':config.get('ArchivesSpace', 'repository'), 'user': config.get('ArchivesSpace', 'user'), 'password': config.get('ArchivesSpace', 'password')}
repositoryBaseURL = '{baseURL}/repositories/{repository}'.format(**dictionary)
publishIDs = config.get('Export', 'publishIDs')

# authenticates the session
auth = requests.post('{baseURL}/users/{user}/login?password={password}&expiring=false'.format(**dictionary)).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session}

# Gets the IDs of all resources in the repository
print 'Getting a list of resources'
resourceIds = requests.get(repositoryBaseURL + '/resources?all_ids=true', headers=headers)

for r in resourceIds.json():
    resource = (requests.get(repositoryBaseURL + '/resources/' + str(r), headers=headers)).json()
    resourceID = resource["id_0"]
    # Publish the resource record if it's in the publish list...
    if resourceID in publishIDs or resourceID.startswith('LI'):
        resource["publish"] = True
        updated = requests.post(repositoryBaseURL + '/resources/' + str(r), headers=headers, data=json.dumps(resource))
        print resourceID + ' published'
    # ...otherwise unpublish the resource record
    else:
        resource["publish"] = False
        updated = requests.post(repositoryBaseURL + '/resources/' + str(r), headers=headers, data=json.dumps(resource))
        print resourceID + ' unpublished'
print 'Done!'
