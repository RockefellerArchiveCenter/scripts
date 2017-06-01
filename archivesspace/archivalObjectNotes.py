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

def findResourceId(headers):
# Gets the parent resource id_0 for each archival object
	try:
		uri = ao["resource"].get('ref')
		resource = (requests.get(resourceURL + str(uri), headers=headers)).json()
		global resourceID
		resourceID = resource["id_0"]
		return resourceID
	except:
		pass

def findWordsInNotes(n):
	search_words = ['obsolete','digital','special format','equipment','computer']
	try:
		for note_type in note_list:
			if n["type"] == note_type:
				for subnote in n["subnotes"]:
					note_text = subnote["content"]
					if any(x in note_text for x in search_words):
						return True	
					else:
						return False
			else:
				return False
	except:
		pass

def getNoteContents(notes, note_type):
	for note in notes:
		try:
			if note["type"] == note_type:
				print "found " + note["type"] + " note"
				if note["jsonmodel_type"] == "note_singlepart":
					return note["content"].decode('utf-8')
				else:
					return note["subnotes"][0]["content"].decode('utf-8')		
		except:
			pass
		
def makeRow(notes,component_title,parent_record,level,refid):
	row = []
	row.append(component_title.encode('utf-8'))
	row.append(parent_record.encode('utf-8'))
	row.append(level.encode('utf-8'))
	row.append(refid.encode('utf-8'))
	for note_type in note_list:
		result_note = getNoteContents(notes, note_type)
		if result_note:
			print result_note
			row.append(result_note.encode('utf-8'))
		else:
			row.append(" ")
	writer.writerow(row)

def findNote(headers,resourceID):
	row = []
	notes = ao["notes"]
	parent_record = resourceID
	level = ao["level"]
	refid = ao["ref_id"]
	try:
		ao["title"].decode('utf-8')
		component_title = ao["title"]
	except:
		component_title = "no title present"
	if notes:
		for n in notes:
			if findWordsInNotes(n):
				print "==========================================="
				print component_title
				makeRow(notes,component_title,parent_record,level,refid)
						

print 'Creating a csv'
spreadsheet = 'object-access-notes.csv'
writer = csv.writer(open(spreadsheet, 'w'))
note_list = ['accessrestrict','odd','altformavail','originalsloc','phystech','processinfo','relatedmaterial','separatedmaterial','dimensions','summary','extent','note','physdesc','physloc','materialspec','physfacet',]
column_headings = ['title','resource','level','refid'] + note_list
print column_headings
writer.writerow(column_headings)


print 'Getting a list of archival objects'
aoIds = requests.get(repositoryBaseURL + '/archival_objects?all_ids=true', headers=headers)
for aoId in aoIds.json():
	ao = (requests.get(repositoryBaseURL + '/archival_objects/' + str(aoId), headers=headers)).json()
	findNote(headers,findResourceId(headers))
spreadsheet.close()
