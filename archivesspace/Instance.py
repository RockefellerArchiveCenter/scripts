#!/usr/bin/env python

import os, requests, json, sys, logging, csv

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

column_names = ['keep_uri', 'replace_uri']
data = pandas.read_csv('containers.csv', names=column_names)

replace_containers = data.replace_uri.tolist()
keep_containers = data.keep_uri.tolist()
resource_containers = []




# authenticates the session
auth = requests.post('{baseURL}/users/{user}/login?password={password}&expiring=false'.format(**dictionary)).json()
session = auth['session']
headers = {'X-ArchivesSpace-Session':session}





def promptForIdentifier():
	identifier = raw_input("Please enter an ArchivesSpace resource identifier: ")
	if identifier:
		return identifier
	else:
		print "You didn't enter anything!"
		promptForIdentifier()


# get a list of identifers
def getArchivalobjectsID (identifier, archival_objects, instances)
		tree = requests.get(respositoryBaseURL + "/resources" + identifier + "/instances", headers=headers).json()
		AOIDS = ao(tree["instances"], archival_objects)
		return AOIDS


#This wil get get the data from the archival object URL
def checkInstanceType (Moving Images, Audio)
	Moving Images = ao["Moving Images"]
	Audio = ao ["Audio"]
	if instance 



def MakeList ResourceList (headers)
	instances = ao["instances"]
	for index, n in enumerate(instances):






def deduplicates_list (Resources URI)
	instances = ao["instances"]




def getResourceData


print 'Creating a csv' 
