#!/usr/bin/env python

import os, requests, json, sys, logging, ConfigParser, pandas

config = ConfigParser.ConfigParser()
config.read('local_settings.cfg')

# Logging configuration
logging.basicConfig(filename=config.get('Logging', 'filename'),format=config.get('Logging', 'format', 1), datefmt=config.get('Logging', 'datefmt', 1), level=config.get('Logging', 'level', 0))
# Sets logging of requests to WARNING to avoid unneccessary info
logging.getLogger("requests").setLevel(logging.WARNING)

dictionary = {'baseURL': config.get('ArchivesSpace', 'baseURL'), 'repository':config.get('ArchivesSpace', 'repository'), 'user': config.get('ArchivesSpace', 'user'), 'password': config.get('ArchivesSpace', 'password')}
repositoryBaseURL = '{baseURL}/repositories/{repository}'.format(**dictionary)
baseURL = '{baseURL}'.format(**dictionary)

column_names = ['keep_uri', 'replace_uri']
data = pandas.read_csv('locations_uris.csv', names=column_names)

replace_locations = data.replace_uri.tolist()
keep_locations = data.keep_uri.tolist()

print replace_locations

# authenticates the session
auth = requests.post('{baseURL}/users/{user}/login?password={password}&expiring=false'.format(**dictionary)).json()
headers = {'X-ArchivesSpace-Session':auth['session']}

def checkContainer(container_data, containerId, headers):
	if len(container_data['container_locations']) > 0:
		for location in container_data['container_locations']:
			for index, location_uri in enumerate(replace_locations):
				if location['ref'] == location_uri:
					location['ref'] = keep_locations[index]
					post = requests.post(repositoryBaseURL + '/top_containers/' + str(containerId), headers=headers, data=json.dumps(container_data))
					if(post.status_code == requests.codes.ok):
						print 'Location '+replace_locations[index]+' was replaced with location '+keep_locations[index]+' in top container '+str(containerId)
						logging.info('Location '+replace_locations[index]+' was replaced with location '+keep_locations[index]+' in top container '+str(containerId))
					else:
						print post.text
						logging.error(post.text)
	else:
		pass

print 'Getting a list of containers'
containerIds = requests.get(repositoryBaseURL + '/top_containers?all_ids=true', headers=headers).json()
logging.info('***** Find and replace operation started *****')
for containerId in containerIds:
	container = requests.get(repositoryBaseURL + '/top_containers/' + str(containerId), headers=headers).json()
	print 'Checking container ' + str(containerId)
	checkContainer(container, containerId, headers)
logging.info('***** Find and replace operation ended *****')
