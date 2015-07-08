#!/usr/bin/env python

import os, requests, json, sys, datetime, calendar

# the base URL of your ArchivesSpace installation
baseURL = 'http://asurl:8089'
# the id of your repository
repository = 'repoid'
# the username to authenticate with
user = 'username'
# the password for the username above
password = 'password'
# export destinations, should end with a trailing slash
EADdestination = '/path/to/export/location/'
if not os.path.exists(EADdestination):
    os.makedirs(EADdestination)
METSdestination = '/path/to/export/location/'
if not os.path.exists(METSdestination):
    os.makedirs(METSdestination)
# EAD Export options
exportUnpublished = 'false'
exportDaos = 'true'
exportNumbered = 'false'
exportPdf = 'false'
# Unix time of last export
lastExport = max(os.path.getmtime(root) for root,_,_ in os.walk(EADdestination))
# URI list (to be populated by URIs of exported resource records)
uriList = []

# authenticates the session
auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
headers = {'X-ArchivesSpace-Session':auth["session"]}

# Gets the IDs of all resources in the repository'
resourceIds = requests.get(baseURL + '/repositories/'+repository+'/resources?all_ids=true', headers=headers)

# Exports EAD for published resources updated since last export
for id in resourceIds.json():
     resource = (requests.get(baseURL + '/repositories/'+repository+'/resources/' + str(id), headers=headers)).json()
     updated = calendar.timegm(datetime.datetime.strptime(resource["user_mtime"], "%Y-%m-%dT%H:%M:%SZ").timetuple())
     resourceID = resource["id_0"]
     if updated > lastExport and resource["publish"]:
        print 'Exporting ' + resourceID + ' to ' + EADdestination,
        ead = requests.get(baseURL + '/repositories/'+repository+'/resource_descriptions/'+str(id)+'.xml?include_unpublished='+exportUnpublished+'&include_daos='+exportDaos+'&numbered_cs='+exportNumbered+'&print_pdf='+exportPdf, headers=headers, stream=True)
        with open(EADdestination+resourceID+'.xml', 'wb') as f:
            for chunk in ead.iter_content(102400):
                f.write(chunk)
        f.close
        print '... done!'
        uriList.append(resource["uri"])
print 'All updated and published finding aids exported!'
print uriList

if len(uriList) > 0:
    # Gets the IDs of all digital objects in the repository
    doIds = requests.get(baseURL + '/repositories/'+repository+'/digital_objects?all_ids=true', headers=headers)

    #Export METS for digital objects
    for id in doIds.json():
        digital_object = (requests.get(baseURL + '/repositories/'+repository+'/digital_objects/' + str(id), headers=headers)).json()
        doID = digital_object["digital_object_id"]
        if digital_object["linked_instances"]:
            component = (requests.get(baseURL + digital_object["linked_instances"][0]["ref"], headers=headers)).json()
            # Get the URI for the resource
            if component["jsonmodel_type"] == 'resource':
                resource = digital_object["linked_instances"][0]["ref"]
            else:
                resource = component["resource"]["ref"]
            if resource in uriList:
                print 'Exporting ' + doID + ' to ' + METSdestination,
                mets = requests.get(baseURL + '/repositories/'+repository+'/digital_objects/mets/'+str(id)+'.xml', headers=headers).text
                f = open(METSdestination+doID+'.xml', 'w')
                f.write(mets.encode('utf-8'))
                f.close
                print '... done!'
    print 'All METS records associated with updated and published finding aids exported'
print 'All done!'
#And now, for our next trick, version in Git
