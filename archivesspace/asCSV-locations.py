#!/usr/bin/env python

import os, requests, json, logging, ConfigParser, csv
from codecs import encode
from codecs import decode

config = ConfigParser.ConfigParser()
config.read('local_settings.cfg')

# Logging configuration
logging.basicConfig(filename=config.get('Logging', 'filename'),format=config.get('Logging', 'format', 1), datefmt=config.get('Logging', 'datefmt', 1), level=config.get('Logging', 'level', 0))
# Sets logging of requests to WARNING to avoid unneccessary info
logging.getLogger("requests").setLevel(logging.WARNING)

dictionary = {'baseURL': config.get('ArchivesSpace', 'baseURL'), 'repository':config.get('ArchivesSpace', 'repository'), 'user': config.get('ArchivesSpace', 'user'), 'password': config.get('ArchivesSpace', 'password')}
repositoryBaseURL = '{baseURL}/repositories/{repository}'.format(**dictionary)
baseURL = '{baseURL}'.format(**dictionary)

# authenticates the session
auth = requests.post('{baseURL}/users/{user}/login?password={password}&expiring=false'.format(**dictionary)).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session}

#creates the spreadsheet
writer = csv.writer(open('locations.csv', 'w'))

def make_row(data):
	row = []
	row.append(data['building'] if 'building' in data else '')
	row.append(data['floor'] if 'floor' in data else '')
	row.append(data['room']if 'room' in data else '')
	row.append(data['coordinate_1_label'] if 'coordinate_1_label' in data else '')
	row.append(data['coordinate_1_indicator'] if 'coordinate_1_indicator' in data else '')
	row.append(data['coordinate_2_label'] if 'coordinate_2_label' in data else '')
	row.append(data['coordinate_2_indicator'] if 'coordinate_2_indicator' in data else '')
	row.append(data['uri'])
	writer.writerow(row)

def main():
	column_headings = ['building','floor','room','coordinate_1_label','coordinate_1_indicator','coordinate_2_label','coordinate_2_indicator','uri']
	writer.writerow(column_headings)
	locationIds = requests.get(baseURL + '/locations?all_ids=true', headers=headers)
	for locationId in locationIds.json():
		location = (requests.get(baseURL + '/locations/' + str(locationId), headers=headers)).json()
		print 'Writing location', str(locationId)
		make_row(location)

main()
