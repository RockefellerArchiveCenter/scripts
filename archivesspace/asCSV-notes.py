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

dictionary = {'base_url': config.get('ArchivesSpace', 'baseURL'), 'repository':config.get('ArchivesSpace', 'repository'), 'user': config.get('ArchivesSpace', 'user'), 'password': config.get('ArchivesSpace', 'password')}
repository_base_url = '{base_url}/repositories/{repository}'.format(**dictionary)

# authenticates the session
auth = requests.post('{base_url}/users/{user}/login?password={password}&expiring=false'.format(**dictionary)).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session}

def get_note_text(data):
	for note in data["notes"]:
		try:
			if note["type"] == note_type:
				print 'Writing ' + note_type + ' from ' + data["jsonmodel_type"] + ' ' + data["id_0"]
				if note["jsonmodel_type"] == "note_singlepart":
					make_row(note["content"])
				else:
					make_row(note["subnotes"][0]["content"])
		except:
			pass

def make_row(note_text):
	row = []
	row.append(note_text)
	writer.writerow(row)

# have user enter note type
note_type = raw_input('Enter note type: ')

print 'Creating a csv'
spreadsheet = 'notes.csv'
writer = csv.writer(open(spreadsheet, 'w'))

print 'Getting a list of resources'
resource_ids = requests.get(repository_base_url + '/resources?all_ids=true', headers=headers)
for resource_id in resource_ids.json():
	resource = (requests.get(repository_base_url + '/resources/' + str(resource_id), headers=headers)).json()
	if resource["id_0"].startswith("FA"):
		get_note_text(resource)
print 'Getting a list of archival objects'
ao_ids = requests.get(repository_base_url + '/archival_objects?all_ids=true', headers=headers)
for ao_id in ao_ids.json():
	ao = (requests.get(repository_base_url + '/archival_objects/' + str(ao_id), headers=headers)).json()
	if ao["notes"]:
		get_note_text(ao)
print 'Done!'
