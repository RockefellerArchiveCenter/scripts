#!/usr/bin/env python

import os, requests, json, sys, logging, ConfigParser, urllib2, csv
from codecs import encode
from codecs import decode

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

# authenticates the session
auth = requests.post('{baseURL}/users/{user}/login?password={password}&expiring=false'.format(**dictionary)).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session}

def getNoteText(data):
	for note in data["notes"]:
		try:
			if note["type"] == note_type:
				print 'Writing ' + note_type + ' from ' + data["jsonmodel_type"] + ' ' + data["id_0"]
				if note["jsonmodel_type"] == "note_singlepart":
					makeRow(note["content"])
				else:
					makeRow(note["subnotes"][0]["content"])
		except:
			pass

def makeRow(note_text):
	row = []
	row.append(note_text)
	writer.writerow(row)

# have user enter note type
note_type = raw_input('Enter note type: ')

print 'Creating a csv'
spreadsheet = 'notes.csv'
writer = csv.writer(open(spreadsheet, 'w'))

print 'Getting a list of resources'
resourceIds = requests.get(repositoryBaseURL + '/resources?all_ids=true', headers=headers)
for resourceId in resourceIds.json():
	resource = (requests.get(repositoryBaseURL + '/resources/' + str(resourceId), headers=headers)).json()
	if resource["id_0"].startswith("FA"):
		getNoteText(resource)
print 'Getting a list of archival objects'
aoIds = requests.get(repositoryBaseURL + '/archival_objects?all_ids=true', headers=headers)
for aoId in aoIds.json():
	ao = (requests.get(repositoryBaseURL + '/archival_objects/' + str(aoId), headers=headers)).json()
	if ao["notes"]:
		getNoteText(ao)
print 'Done!'
