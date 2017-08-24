#!/usr/bin/env python

import os, requests, json, sys, logging, ConfigParser, pandas, csv

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

#initialize dictionary for containers with barcodes without periods
keep_dict = {}

bad_dict = {}

#initialize dictionary for containers with barcodes with periods or empty barcodes
duplicates_list = []

#initialize dictionary with top_container refs to use for replacement
replace_dict = {}

# authenticates the session
auth = requests.post('{baseURL}/users/{user}/login?password={password}&expiring=false'.format(**dictionary)).json()
session = auth['session']
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

def makeDuplicatesList(headers):
	instances = ao["instances"]
	for index, n in enumerate(instances):
		global type1
		type1 = "0"
		global indicator1
		indicator1 = "0"
		global ref1
		ref1 = n["sub_container"]["top_container"]["ref"]
		global location1
		location1 ="0"
		global loc_ref
		loc_ref = "0"
		global ind_type
		ind_type = "0"
		top_container_json = requests.get('{baseURL}'.format(**dictionary) + ref1, headers=headers).json()
		try:
			type1 = top_container_json["type"]
		except:
			pass
		try:
			indicator1 = top_container_json["indicator"]
		except:
			pass
		if "barcode" not in top_container_json or len(top_container_json["barcode"]) == 0 or "." in top_container_json["barcode"]:
			duplicates_list.append(ref1)
			print duplicates_list

#creates dictionarry of valid top_containers with locations
def makeLocationsDict(headers):
	instances = ao["instances"]
	for index, n in enumerate(instances):
		global type1
		type1 = "0"
		global indicator1
		indicator1 = "0"
		global ref1
		ref1 = n["sub_container"]["top_container"]["ref"]
		global location1
		location1 ="0"
		global loc_ref
		loc_ref = "0"
		global ind_type
		ind_type = "0"
		top_container_json = requests.get('{baseURL}'.format(**dictionary) + ref1, headers=headers).json()
		if n["instance_type"] == "digital_object":
			pass
		else:
			try:
				type1 = top_container_json["type"]
			except:
				pass
			try:
				indicator1 = top_container_json["indicator"]
			except:
				pass
			ind_type = indicator1 + type1
			if "barcode" not in top_container_json:
				bad_dict[ref1] = ind_type
			elif len(top_container_json["barcode"]) > 0 and "." not in top_container_json["barcode"]:
				keep_dict[ind_type] = ref1
			elif len(top_container_json["barcode"]) == 0 or "." in top_container_json["barcode"]:
				bad_dict[ref1] = ind_type

def makeCSV():
	writer=csv.writer(open('dict.csv', 'wb'))
	for tpref in list(set(duplicates_list)):
		writer.writerow([tpref])

#creates dictionary of top_container ref key value pairs for replacement
def checkLocationsDict():
	#print keep_dict
	for key,value in bad_dict.iteritems():
		if value in keep_dict:
			#print value
			for x,y in keep_dict.iteritems():
				if value == x:
					new_container = y
					replace_dict[key] = new_container
					#print replace_dict
				else:
					pass
		else:
			pass

#reads through replace_dict and updates top container ref when it finds a match
def replaceTopContainer(ao, aoId, headers):
	global replaced
	replaced = "0"
	global original
	original ="0"
	if len(ao['instances']) > 0:
		for n, instance in enumerate(ao['instances']):
			if ao["instances"][n]["instance_type"] == "digital_object":
				pass
			elif ao["instances"][n]["sub_container"]["top_container"]["ref"] in replace_dict:
				replaced = ao["instances"][n]["sub_container"]["top_container"]["ref"]
				original = replace_dict[ao["instances"][n]["sub_container"]["top_container"]["ref"]]
				ao["instances"][n]["sub_container"]["top_container"]["ref"] = replace_dict[ao["instances"][n]["sub_container"]["top_container"]["ref"]]
				post = requests.post('{baseURL}'.format(**dictionary) + str(aoId), headers=headers, data=json.dumps(ao))
				print 'Container '+replaced+' was replaced with container '+original+' in archival object '+str(aoId)
				logging.info('Container '+replaced+' was replaced with container '+original+' in archival object '+str(aoId))
			else:
				pass
	else:
		pass

identifier = promptForIdentifier()
listreplace = raw_input('Would you like to run the replace operation or obtain a csv of duplicate objects? (replace/list)')
print 'Getting a list of archival objects'
aoIds = getResourceObjects(identifier, headers, resource_containers)
print aoIds
logging.info('Find and replace operation started')
if listreplace == 'replace':
	for aoId in aoIds:
		ao = (requests.get('{baseURL}'.format(**dictionary) + str(aoId), headers=headers)).json()
		print 'Checking archival object ' + str(aoId)
		makeLocationsDict(headers)
	checkLocationsDict()
	for aoId in aoIds:
		ao = (requests.get('{baseURL}'.format(**dictionary) + str(aoId), headers=headers)).json()
		replaceTopContainer(ao, aoId, headers)
elif listreplace == 'list':
	for aoId in aoIds:
		ao = (requests.get('{baseURL}'.format(**dictionary) + str(aoId), headers=headers)).json()
		print 'Checking archival object ' + str(aoId)
		makeDuplicatesList(headers)
	makeCSV()
logging.info('Find and replace operation ended')
