#!/usr/bin/env python

import os, requests, json, sys, logging, ConfigParser, urllib2

config = ConfigParser.ConfigParser()
config.read('local_settings.cfg')

# Logging configuration
logging.basicConfig(filename=config.get('Logging', 'filename'),format=config.get('Logging', 'format', 1), datefmt=config.get('Logging', 'datefmt', 1), level=config.get('Logging', 'level', 0))
# Sets logging of requests to WARNING to avoid unneccessary info
logging.getLogger("requests").setLevel(logging.WARNING)

dictionary = {'baseURL': config.get('ArchivesSpace', 'baseURL'), 'repository':config.get('ArchivesSpace', 'repository'), 'user': config.get('ArchivesSpace', 'user'), 'password': config.get('ArchivesSpace', 'password')}
repositoryBaseURL = '{baseURL}/repositories/{repository}'.format(**dictionary)
resourceURL = '{baseURL}'.format(**dictionary)

# authenticates the session
auth = requests.post('{baseURL}/users/{user}/login?password={password}&expiring=false'.format(**dictionary)).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session}

def findOrphans(container, containerId, headers):
    if len(container["collection"]) > 0:
        print str(containerId) + ' will stay'
    else:
        print str(containerId) + ' will be deleted'
        deleted = requests.delete(repositoryBaseURL + '/top_containers/' + str(containerId), headers=headers, data=json.dumps(container))
        logging.info(str(containerId) + ' was deleted')

print 'Getting a list of top containers'
containerIds = requests.get(repositoryBaseURL + '/top_containers?all_ids=true', headers=headers)
for containerId in containerIds.json():
    container = (requests.get(repositoryBaseURL + '/top_containers/' + str(containerId), headers=headers)).json()
    findOrphans(container, containerId, headers)
