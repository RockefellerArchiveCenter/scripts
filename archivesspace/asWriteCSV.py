#!/usr/bin/env python

import os, requests, json, sys, logging, ConfigParser, pandas, csv
reload(sys)
sys.setdefaultencoding('utf-8')
from codecs import encode

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
session = auth['session']
headers = {'X-ArchivesSpace-Session':session}

resource_containers = []

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

def makeCSV():
	writer=csv.writer(open('Reports.csv', 'wb'))
	for tpref in list(set(duplicates_list)):
		writer.writerow([tpref])

def getAOInfo(headers):
	global title
	global refid
	global begindate
	begindate = "0"
	global enddate
	enddate = "0"
	global notecontent
	notecontent = "0"
	title = ao["title"]
	dates = ao["dates"]
	refid = ao["ref_id"]
	notes = ao["notes"]
	for index, n in enumerate(dates):
		try:
			begindate = n["begin"]
		except:
			pass
		try:
			 enddate = n["end"]
		except:
			 pass
	for index, n in enumerate(notes):
		try:
			if n["type"] == "accessrestrict":
				for subnote in n["subnotes"]:
					notecontent = subnote["content"]
		except:
			notecontent = "FALSE"
	print title
	print begindate
	print enddate
	print refid
	print notecontent

def writeCSV():
	myfile = open("CatReports.csv", "wb")
	row = [title ,begindate ,enddate ,refid ,notecontent]
	writer.writerow(row)
	myfile.close

identifier = promptForIdentifier()
aoIds = getResourceObjects(identifier, headers, resource_containers)
print aoIds
writer = csv.writer(open("CatReports.csv", "wb"))
column_headings = ["title", "begindate", "enddate", "refid", "accessrestrict"]
writer.writerow(column_headings)
logging.info('Writing to CSV started')
for aoId in aoIds:
	ao = (requests.get('{baseURL}'.format(**dictionary) + str(aoId), headers=headers)).json()
	getAOInfo(headers)
	writeCSV()
logging.info('Find and replace operation ended')
