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

# authenticates the session
auth = requests.post('{baseURL}/users/{user}/login?password={password}&expiring=false'.format(**dictionary)).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session}

def findResourceId (headers):
# Gets the resource id_0 for each archival object
    try:
        uri = ao["resource"].get('ref')
        resource = (requests.get(resourceURL + str(uri), headers=headers)).json()
        global resourceID
        resourceID = resource["id_0"]
        #print resourceID
    except:
        logging.warning('Archival Object ' + str(aoId) + ' is not connected to a resource and will be skipped')
        resourceID = 'Archival Object is not associated with a resource and will be skipped'

def findBoxFolder(headers):
# Gets the box and folder number of each instance
    instances = ao["instances"]
    for index, n in enumerate(instances):
        global ctypeone
        global cindicatorone
        global ctypetwo
        global cindicatortwo
        global boxfolder
        ctypeone = 0
        cindicatorone = 0
        ctypetwo = 0
        cindicatortwo = 0
        try:
            ctypeone = n["container"]["type_1"]
        except:
            pass
        try:
            cindicatorone = n["container"]["indicator_1"]
        except:
            pass
        try:
            ctypetwo = n["container"]["type_2"]
        except:
            pass
        try:
            cindicatortwo = n["container"]["indicator_2"]
        except:
            pass
        if (ctypeone == 0 and cindicatorone == 0):
            boxfolder = 'But no containers found'
        elif (ctypeone != 0 and cindicatorone != 0 and ctypetwo == 0 and cindicatortwo == 0):
            boxfolder = u' '.join((ctypeone, cindicatorone)).encode('utf-8').strip()
        elif (ctypeone != 0 and cindicatorone != 0 and ctypetwo != 0 and cindicatortwo != 0):
            boxfolder = u' '.join((ctypeone, cindicatorone, ctypetwo, cindicatortwo)).encode('utf-8').strip()

def deleteNotes(headers):
# Deletes AccessRestrict notes that match input notecontent
    notes = ao["notes"]
    for index, n in enumerate(notes):
        try:
            if n["type"] == notetype:
                for subnote in n["subnotes"]:
                    if notecontent == subnote["content"] and boxfolder != []:
                        del notes[index]
                        updated = requests.post(repositoryBaseURL + '/archival_objects/' + str(aoId), headers=headers, data=json.dumps(ao))
                        logging.info('Deleted access restrict note with ' + str(notecontent) + ' content from archival object ' + str(aoId) + ' in resource ' + str(resourceID) + ' from ' + str(boxfolder))
                    elif notecontent == subnote["content"] and boxfolder == []:
                        del notes[index]
                        updated = requests.post(repositoryBaseURL + '/archival_objects/' + str(aoId), headers=headers, data=json.dumps(ao))
                        logging.info('Deleted access restrict note with ' + str(notecontent) + ' content from archival object ' + str(aoId) + ' in resource ' + str(resourceID) + ' with no instances')
        except:
            pass

def replaceNotes(headers):
# Deletes AccessRestrict notes that match input notecontent
    notes = ao["notes"]
    for index, n in enumerate(notes):
        try:
            if n["type"] == notetype:
                for subnote in n["subnotes"]:
                    if notecontent == subnote["content"] and boxfolder != []:
                        subnote["content"] = replacecontent
                        updated = requests.post(repositoryBaseURL + '/archival_objects/' + str(aoId), headers=headers, data=json.dumps(ao))
                        logging.info('Replacing note with ' + str(notecontent) + ' content with ' + str(replacecontent) + ' content in archival object ' + str(aoId) + ' in resource ' + str(resourceID) + ' from ' + str(boxfolder))
                    elif notecontent == subnote["content"] and boxfolder == []:
                        subnote["content"] = replacecontent
                        updated = requests.post(repositoryBaseURL + '/archival_objects/' + str(aoId), headers=headers, data=json.dumps(ao))
                        logging.info('Replacing note with ' + str(notecontent) + ' content with ' + str(replacecontent) + ' content in archival object ' + str(aoId) + ' in resource ' + str(resourceID) + ' with no instances')
        except:
            pass

#asks user to input note content
resourcesearch = raw_input('Enter resorce id number: ')
objectlevel = raw_input('Enter archival object level: ')
notetype = raw_input('Enter the type of note (use EAD note types, e.g. accessrestrict): ')
notecontent = raw_input('Enter note content: ')
modifydelete = raw_input('Modify notes or delete notes? (modify/delete) ')
if modifydelete == 'modify':
    replacecontent = raw_input('New note content: ')
print 'Getting a list of archival objects'
aoIds = requests.get(repositoryBaseURL + '/archival_objects?all_ids=true', headers=headers)
for aoId in aoIds.json():
    ao = (requests.get(repositoryBaseURL + '/archival_objects/' + str(aoId), headers=headers)).json()
    boxfolder = []
    findResourceId(headers)
    findBoxFolder(headers)
    levels = ao["level"]
    if  modifydelete == 'delete' and resourceID != 'Archival Object is not associated with a resource and will be skipped' and resourceID == resourcesearch and levels == objectlevel:
        deleteNotes(headers)
    elif modifydelete == 'modify' and resourceID != 'Archival Object is not associated with a resource and will be skipped' and resourceID == resourcesearch and levels == objectlevel:
        replaceNotes(headers)
