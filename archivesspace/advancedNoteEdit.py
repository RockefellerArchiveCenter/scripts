#!/usr/bin/env python

import os, requests, json, sys, logging, ConfigParser, urllib2

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

resource_containers = []

# authenticates the session
auth = requests.post('{baseURL}/users/{user}/login?password={password}&expiring=false'.format(**dictionary)).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session}

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

def deleteNotes(headers):
# Deletes AccessRestrict notes that match input notecontent
    notes = ao["notes"]
    for index, n in enumerate(notes):
        try:
            if n["type"] == notetype:
                for subnote in n["subnotes"]:
                    if notecontent == subnote["content"]:
                        del notes[index]
                        post = requests.post('{baseURL}'.format(**dictionary) + str(aoId), headers=headers, data=json.dumps(ao))
                        logging.info('Deleted note with ' + str(notecontent) + ' content from archival object ' + str(aoId) + ' in resource ' + str(resourceID))
        except:
            pass

def replaceNotes(headers):
# Deletes AccessRestrict notes that match input notecontent
    notes = ao["notes"]
    for index, n in enumerate(notes):
        try:
            if n["type"] == notetype:
                for subnote in n["subnotes"]:
                    if notecontent == subnote["content"]:
                        subnote["content"] = replacecontent
                        post = requests.post('{baseURL}'.format(**dictionary) + str(aoId), headers=headers, data=json.dumps(ao))
                        logging.info('Replacing note with ' + str(notecontent) + ' content with ' + str(replacecontent) + ' content in archival object ' + str(aoId) + ' in resource ' + str(resourceID))
        except:
            pass

#asks user to input note content
identifier = promptForIdentifier()
objectlevel = raw_input('Enter archival object level: ')
notetype = raw_input('Enter the type of note (use EAD note types, e.g. accessrestrict): ')
notecontent = raw_input('Enter note content: ')
modifydelete = raw_input('Modify notes or delete notes? (modify/delete) ')
if modifydelete == 'modify':
    replacecontent = raw_input('New note content: ')
print 'Getting a list of archival objects'
aoIds = getResourceObjects(identifier, headers, resource_containers)
for aoId in aoIds:
    ao = (requests.get('{baseURL}'.format(**dictionary) + str(aoId), headers=headers)).json()
    boxfolder = []
    levels = ao["level"]
    if  modifydelete == 'delete' and levels == objectlevel:
        deleteNotes(headers)
    elif modifydelete == 'modify' and levels == objectlevel:
        replaceNotes(headers)
