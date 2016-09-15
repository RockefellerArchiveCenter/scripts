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
resourceURL = '{baseURL}'.format(**dictionary)

column_names = ['keep_uri', 'replace_uri']
data = pandas.read_csv('containers.csv', names=column_names)

replace_containers = data.replace_uri.tolist()
keep_containers = data.keep_uri.tolist()
resource_containers = []

# authenticates the session
auth = requests.post('{baseURL}/users/{user}/login?password={password}&expiring=false'.format(**dictionary)).json()
headers = {'X-ArchivesSpace-Session':auth['session']}

def promptForIdentifier():
	identifier = raw_input("Please enter a resource identifier: ")
	if identifier:
		return identifier
	else:
		print "You didn't enter anything!"
		promptForIdentifier()

def getResourceObjects(identifier, headers, resource_containers):
	tree = requests.get(repositoryBaseURL + "/resources/" + identifier + "/tree", headers=headers).json()
	refList = getRefs(tree["children"], resource_containers)
	return refList

def getRefs(data, resource_containers):
	for component in data:
		resource_containers.append(component["record_uri"])
		if component["has_children"]:
			getRefs(component["children"], resource_containers)
	return resource_containers

def checkArchivalObject(archival_object, aoUri, headers):
	if len(archival_object['instances']) > 0:
		for instance in archival_object['instances']:
			for index, container_uri in enumerate(replace_containers):
				if ('sub_container' in instance):
					if (instance['sub_container']['top_container']['ref'] == container_uri):
						instance['sub_container']['top_container']['ref'] = keep_containers[index]
						post = requests.post('{baseURL}'.format(**dictionary) + str(aoUri), headers=headers, data=json.dumps(archival_object))
						if(post.status_code == requests.codes.ok):
							print 'Container '+replace_containers[index]+' was replaced with container '+keep_containers[index]+' in archival object '+str(aoUri)
							logging.info('Container '+replace_containers[index]+' was replaced with container '+keep_containers[index]+' in archival object '+str(aoUri))
						else:
							print post.text
							logging.error(post.text)
	else:
		pass

if not len(sys.argv) > 1:
	identifier = promptForIdentifier()
else:
	identifier = sys.argv[1]
print 'Getting a list of archival objects'
aoUris = getResourceObjects(identifier, headers, resource_containers)
logging.info('Find and replace operation started')
for aoUri in aoUris:
	ao = (requests.get('{baseURL}'.format(**dictionary) + str(aoUri), headers=headers)).json()
	print 'Checking archival object ' + str(aoUri)
	checkArchivalObject(ao, aoUri, headers)
logging.info('Find and replace operation ended')
