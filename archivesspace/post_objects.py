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
resourceURL = '{baseURL}'.format(**dictionary)

# authenticates the session
auth = requests.post('{baseURL}/users/{user}/login?password={password}'.format(**dictionary)).json()
headers = {'X-ArchivesSpace-Session': auth["session"]}

def post_data(object_data, object_type):
	post_response = requests.post('{}/{}s'.format(repositoryBaseURL, object_type), headers=headers, data=object_data).json()
	print post_response

def get_data():
	file = raw_input("Enter JSON object path: ")
	if os.path.isfile(file):
		with open (file) as json_data:
			return json.load(json_data)
	else:
		print "You didn't enter anything!"
		get_data()

def get_type(json):
	type = json['jsonmodel_type']
	return type

data = get_data()
type = get_type(data)
post_data(data, type)
