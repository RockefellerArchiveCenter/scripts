#!/usr/bin/env python

import os, requests, json, sys, logging, ConfigParser
# from codecs import encode
# from codecs import decode

config = ConfigParser.ConfigParser()
config.read('local_settings.cfg')

# Logging configuration
logging.basicConfig(filename=config.get('Logging', 'filename'),format=config.get('Logging', 'format', 1), datefmt=config.get('Logging', 'datefmt', 1), level=config.get('Logging', 'level', 0))
# Sets logging of requests to WARNING to avoid unneccessary info
logging.getLogger("requests").setLevel(logging.WARNING)
# Adds randomly generated commit message from external text file
#commitMessage = line = random.choice(open(config.get('Git', 'commitMessageData')).readlines());

dictionary = {'baseURL': config.get('ArchivesSpace', 'baseURL'), 'repository':config.get('ArchivesSpace', 'repository'), 'user': config.get('ArchivesSpace', 'user'), 'password': config.get('ArchivesSpace', 'password')}
repositoryBaseURL = '{baseURL}/repositories/{repository}'.format(**dictionary)
resourceURL = '{baseURL}'.format(**dictionary)

replace_containers = ['/repositories/2/top_containers/132174', '/repositories/2/top_containers/132178']
keep_containers = ['/repositories/2/top_containers/132173', '/repositories/2/top_containers/132177']

# authenticates the session
auth = requests.post('{baseURL}/users/{user}/login?password={password}&expiring=false'.format(**dictionary)).json()
session = auth['session']
headers = {'X-ArchivesSpace-Session':session}

def checkArchivalObject(archival_object, aoId, headers):
	if len(archival_object['instances']) > 0:
		for instance in archival_object['instances']:
			for index, container_uri in enumerate(replace_containers):
				if ('sub_container' in instance):
					if (instance['sub_container']['top_container']['ref'] == container_uri):
						instance['sub_container']['top_container']['ref'] = keep_containers[index]
						print archival_object
						post = requests.post(repositoryBaseURL + '/archival_objects/'+str(aoId), headers=headers, data=json.dumps(archival_object))
						print 'Container '+replace_containers[index]+' was replaced with container '+keep_containers[index]+' in archival object '+str(aoId)
						logging.info('Container '+replace_containers[index]+' was replaced with container '+keep_containers[index]+' in archival object '+str(aoId))
	else:
		pass

print 'Getting a list of archival objects'
aoIds = requests.get(repositoryBaseURL + '/archival_objects?all_ids=true', headers=headers).json()
logging.info('Find and replace operation started')
for aoId in reversed(aoIds):
	ao = (requests.get(repositoryBaseURL + '/archival_objects/' + str(aoId), headers=headers)).json()
	print 'Checking archival object ' + str(aoId)
	checkArchivalObject(ao, aoId, headers)
logging.info('Find and replace operation ended')
