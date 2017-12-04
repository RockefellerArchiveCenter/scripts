#!/usr/bin/env python

import os, requests, json, sys, logging, ConfigParser, urllib2, pandas

config = ConfigParser.ConfigParser()
config.read('local_settings.cfg')

# Logging configuration
logging.basicConfig(filename=config.get('Logging', 'filename'),format=config.get('Logging', 'format', 1), datefmt=config.get('Logging', 'datefmt', 1), level=config.get('Logging', 'level', 0))
# Sets logging of requests to WARNING to avoid unneccessary info
logging.getLogger("requests").setLevel(logging.WARNING)

dictionary = {'baseURL': config.get('ArchivesSpace', 'baseURL'), 'repository':config.get('ArchivesSpace', 'repository'), 'user': config.get('ArchivesSpace', 'user'), 'password': config.get('ArchivesSpace', 'password')}
locationURL = '{baseURL}/locations/'.format(**dictionary)

# authenticates the session
auth = requests.post('{baseURL}/users/{user}/login?password={password}&expiring=false'.format(**dictionary)).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session}

locations = pandas.read_csv('locations.csv', header=None)
locs = locations.values.T[0].tolist()

print 'Getting a list of top containers'
for loc in locs:
    print '/locations/' + str(loc) + ' will be deleted'
    location = (requests.get(locationURL + str(loc), headers=headers)).json()
    deleted = requests.delete(locationURL + str(loc), headers=headers, data=json.dumps(location))
    logging.info('/locations/' + str(loc) + ' was deleted')
