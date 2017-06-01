#!/usr/bin/env python

import os, requests, json, sys, logging, ConfigParser, urllib2, csv
from codecs import encode
from codecs import decode

config = ConfigParser.ConfigParser()
config.read('publish_local_settings.cfg')

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

def findWordsInNotes(n):
	search_words = ['obsolete','digital','special format','equipment']
	try:
		for note_type in note_list:
			if n["type"] == note_type:
				for subnote in n["subnotes"]:
					note_text = subnote["content"]
					if any(x in note_text for x in search_words):
						return True	
					else:
						return False
	except:
		pass

def getNoteContents(notes, matching_note):
	for note in notes:
		try:
			if note["type"] == matching_note:
				print "found " + note["type"] + " note"
				if note["jsonmodel_type"] == "note_singlepart":
					return note["content"].decode('utf-8')
				else:
					return note["subnotes"][0]["content"].decode('utf-8')		
		except:
			pass
		
def makeRow(notes,component_title,call_number):
	row = []
	row.append(component_title)
	row.append(call_number)
	for matching_note in note_list:
		matching_note = getNoteContents(notes, matching_note)
		if matching_note:
			row.append(matching_note.encode('utf-8'))
		else:
			row.append(" ")
	writer.writerow(row)

def findNote(headers):
	row = []
	notes = resource["notes"]
	call_number = resource["id_0"]
	component_title = resource["title"]
	if notes:
		for n in notes:
			if findWordsInNotes(n):
				print "~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~"
				print call_number + " - " + component_title
				makeRow(notes,component_title,call_number)
						

print 'Creating a csv'
spreadsheet = 'access-notes.csv'
writer = csv.writer(open(spreadsheet, 'w'))
note_list = ['accessrestrict','odd','altformavail','originalsloc','phystech','processinfo','relatedmaterial','separatedmaterial','dimensions','summary','extent','note','physdesc','physloc','materialspec','physfacet',]
column_headings = ['title','id'] + note_list
writer.writerow(column_headings)


print 'Getting a list of resources'
resourceIds = requests.get(repositoryBaseURL + '/resources?all_ids=true', headers=headers)
for resourceId in resourceIds.json():
	resource = (requests.get(repositoryBaseURL + '/resources/' + str(resourceId), headers=headers)).json()
	findNote(headers)
spreadsheet.close()
