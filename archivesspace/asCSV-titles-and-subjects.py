#!/usr/bin/env python

import os, requests, json, sys, logging, ConfigParser, urllib2, csv
from agentarchives import archivesspace

config = ConfigParser.ConfigParser()
config.read('local_settings.cfg')

# Logging configuration
logging.basicConfig(filename=config.get('Logging', 'filename'),format=config.get('Logging', 'format', 1), datefmt=config.get('Logging', 'datefmt', 1), level=config.get('Logging', 'level', 0))
# Sets logging of requests to WARNING to avoid unneccessary info
logging.getLogger("requests").setLevel(logging.WARNING)

config = {'repository':config.get('ArchivesSpace', 'repository'), 'user': config.get('ArchivesSpace', 'user'), 'password': config.get('ArchivesSpace', 'password'), 'baseURL': config.get('ArchivesSpace', 'url'), 'port': config.get('ArchivesSpace', 'port')}

def compile_data(data):
	for child in data["children"]:
		make_row(child)
		if child["has_children"]:
			compile_data(child)

def make_row(component):
	row = []
	subject_titles = []
	if component["subjects"]:
		for subject in subjects:
			subject_titles.append(subject["title"])
			subject_titles.join("|")
	row.append(component["title"], subject_titles)
	writer.writerow(row)

# have user enter resource identifier
resource_id = raw_input('Enter resource id: ')

print 'Creating a csv'
spreadsheet = 'titles.csv'
writer = csv.writer(open(spreadsheet, 'w'))
client = archivesspace.ArchivesSpaceClient(config["baseURL"], config["user"], config["password"], config["port"], config["repository"])
print 'Getting children of resource ' + resource_id
data = client.get_resource_component_children('repositories/2/resources/'+str(resource_id))
compile_data(data)
print 'Done!'
