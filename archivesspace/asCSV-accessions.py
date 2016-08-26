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

def makeRow(accession):
	row = []
	number = accession['id_0']
	if 'id_1' in accession:
		number = number + '.' + accession['id_1']
	if 'id_2' in accession:
		number = number + '.' + accession['id_2']
	row.append(accession['title'].encode('utf-8'))
	row.append(number.encode('utf-8'))
	row.append(len(accession['instances']))
	writer.writerow(row)

print 'Creating a csv'
spreadsheet = 'accessions.csv'
writer = csv.writer(open(spreadsheet, 'w'))
column_headings = ['title','number','instances']
print column_headings
writer.writerow(column_headings)


print 'Getting a list of accessions'
accessionIds = requests.get(repositoryBaseURL + '/accessions?all_ids=true', headers=headers)
for accessionId in accessionIds.json():
	accession = (requests.get(repositoryBaseURL + '/accessions/' + str(accessionId), headers=headers)).json()
	print 'Writing accession ' + accessionId
	makeRow(accession)
spreadsheet.close()
