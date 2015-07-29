#!/usr/bin/env python

import os, requests, json, sys, time, pickle
from lxml import etree

# the base URL of your ArchivesSpace installation
baseURL = 'http://localhost:8089'
# the id of your repository
repository = '2'
# the username to authenticate with
user = 'admin'
# the password for the username above
password = 'admin'
# export destinations, should end with a trailing slash
EADdestination = '/Users/harnold/Desktop/testEAD/'
if not os.path.exists(EADdestination):
    os.makedirs(EADdestination)
METSdestination = '/Users/harnold/Desktop/testMETS/'
if not os.path.exists(METSdestination):
    os.makedirs(METSdestination)
# EAD Export options
exportUnpublished = 'false'
exportDaos = 'true'
exportNumbered = 'false'
exportPdf = 'false'
# URI lists (to be populated by URIs of exported or deleted resource records)
uriExportList = []
uriDeleteList = []
# stores a variable for the read this from file
lastExportFilepath = 'lastExport.pickle'

# authenticates the session
def authenticate():
    auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
    token = {'X-ArchivesSpace-Session':auth["session"]}
    return token

# formats XML files
def prettyPrintXml(filePath):
    assert filePath is not None
    parser = etree.XMLParser(resolve_entities=False, strip_cdata=False, remove_blank_text=True)
    document = etree.parse(filePath, parser)
    document.write(filePath, pretty_print=True, encoding='utf-8')

# Exports EAD file
def exportEAD(resourceID, id):
    ead = requests.get(baseURL + '/repositories/'+repository+'/resource_descriptions/'+str(id)+'.xml?include_unpublished='+exportUnpublished+'&include_daos='+exportDaos+'&numbered_cs='+exportNumbered+'&print_pdf='+exportPdf, headers=headers, stream=True)
    with open(EADdestination+resourceID+'.xml', 'wb') as f:
        for chunk in ead.iter_content(102400):
            f.write(chunk)
    f.close
    #validate here
    prettyPrintXml(EADdestination+resourceID+'.xml')

# Exports METS file
def exportMETS(doID):
    print 'Exporting ' + doID + ' to ' + METSdestination
    mets = requests.get(baseURL + '/repositories/'+repository+'/digital_objects/mets/'+str(id)+'.xml', headers=headers).text
    f = open(METSdestination+doID+'.xml', 'w')
    f.write(mets.encode('utf-8'))
    f.close
    #validate here

# Deletes EAD file if it exists
def removeEAD(resourceID, id):
    if os.path.isfile(EADdestination+resourceID+'.xml'):
        print 'Deleting ' + resourceID + '.xml from ' + EADdestination
        os.remove(EADdestination+resourceID+'.xml')
    else:
        print resourceID + '.xml does not exist, skipping'

# Deletes METS file if it exists
def removeMETS(doID):
    print 'Deleting ' + doID + '.xml from ' + METSdestination
    if os.path.isfile(METSdestination+doID+'.xml'):
        print 'Deleting ' + doID + '.xml from ' + METSdestination,
        os.remove(METSdestination+doID+'.xml')
    else:
        print doID + '.xml does not exist, skipping'

def handleResource(resource):
    resourceID = resource["id_0"]
    identifier = resource["uri"].split('/repositories/'+repository+'/resources/',1)[1]
    if resource["publish"]:
        print 'Exporting ' + resourceID + ' to ' + EADdestination
        exportEAD(resourceID, identifier)
        uriExportList.append(resource["uri"])
    else:
        removeEAD(resourceID, identifier)
        uriDeleteList.append(resource["uri"])

def handleDigitalObject(digital_object):
    doID = digital_object["digital_object_id"]
    if digital_object["linked_instances"]:
        component = (requests.get(baseURL + digital_object["linked_instances"][0]["ref"], headers=headers)).json()
        # Get the URI for the resource
        if component["jsonmodel_type"] == 'resource':
            resource = digital_object["linked_instances"][0]["ref"]
        else:
            resource = component["resource"]["ref"]
        if resource in uriExportList:
            exportMETS(doID)
        elif resource in uriDeleteList:
            removeMETS(doID)

headers = authenticate()

with open(lastExportFilepath, 'rb') as pickle_handle:
    lastExport = str(pickle.load(pickle_handle))

with open(lastExportFilepath, 'wb') as pickle_handle:
    pickle.dump(int(time.time()), pickle_handle)

# Gets the IDs of all resources in the repository
resourceIds = requests.get(baseURL + '/repositories/'+repository+'/resources?all_ids=true&modified_since='+str(lastExport), headers=headers)
print 'Looping through resources'
for id in resourceIds.json():
    resource = (requests.get(baseURL + '/repositories/'+repository+'/resources/' + str(id), headers=headers)).json()
    handleResource(resource)
print 'Done with resources'

#gets all archival object ids
archival_objects = requests.get(baseURL + '/repositories/'+repository+'/archival_objects?all_ids=true&modified_since='+str(lastExport), headers=headers)
print 'Looping through archival objects'
for id in archival_objects.json():
    archival_object = requests.get(baseURL + '/repositories/'+repository+'/archival_objects/'+str(id), headers=headers).json()
    resource = (requests.get(baseURL +archival_object["resource"]["ref"], headers=headers)).json()
    if not resource["uri"] in uriExportList and not resource["uri"] in uriDeleteList:
        handleResource(resource)
print 'Done with archival_objects'

if len(uriExportList) > 0 or len(uriDeleteList) > 0:
    # Gets the IDs of all digital objects in the repository
    doIds = requests.get(baseURL + '/repositories/'+repository+'/digital_objects?all_ids=true', headers=headers)
    print 'Looping through digital objects'
    for id in doIds.json():
        digital_object = (requests.get(baseURL + '/repositories/'+repository+'/digital_objects/' + str(id), headers=headers)).json()
        handleDigitalObject(digital_object)
    print 'METS updated!'
    #run script to version
    print 'Versioning files and pushing to Github'
    os.system("./gitVersion.sh")
print 'All done!'
