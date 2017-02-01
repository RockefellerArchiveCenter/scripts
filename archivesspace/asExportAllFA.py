#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import requests
import json
import sys

# set this variables to match the base URL of your ArchivesSpace installation
baseURL = 'http://as.rockarch.org:8089'
# set this variable to match the id of your repository
repository = '2'

include = sys.argv[1]

# authenticates the session
auth = requests.post(baseURL + '/users/USERNAME/login?password=PASSWORD')
json = auth.json() 
session = json["session"]
if auth.status_code == 200:
	print "Authenticated!"
headers = {'X-ArchivesSpace-Session':session}

# Gets the IDs of all resources in the repository
resourceIds = requests.get(baseURL + '/repositories/'+repository+'/resources?all_ids=true', headers=headers)

# Exports EAD for all resources whose IDs contain 'FA'
for id in resourceIds.json():
	resource = (requests.get(baseURL + '/repositories/'+repository+'/resources/' + str(id), headers=headers)).json()
	resourceID = resource["id_0"]
	if include in resourceID:
		ead = requests.get(baseURL + '/repositories/'+repository+'/resource_descriptions/'+str(id)+'.xml', headers=headers).text
		# Sets the location where the files should be saved
		destination = '/Users/harnold/Desktop/ead/'
		f = open(destination+resourceID+'.xml', 'w')
		f.write(ead.encode('utf-8'))
		f.close
		print resourceID + ' exported to ' + destination
