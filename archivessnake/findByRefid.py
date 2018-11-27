#!/usr/bin/env python3

import json, csv, getpass, configparser
from asnake.client import ASnakeClient

def getAo(refid):
    # use find_by_id endpoint
    url = 'repositories/2/find_by_id/archival_objects?ref_id[]=' + refid
    ao = client.get(url).json()
    # get archival object as json
    ao_ref = ao.get("archival_objects")[0].get("ref")
    ao = client.get(ao_ref).json()
    return ao

def getAoTitle(ao):
    # check if archival object has a title
    if ao.get("title"):
        return ao.get("title")
    # if there's no title, use the title of its immediate ancestor
    else:
        ancestor_url = ao.get("ancestors")[0].get("ref")
        ancestor = client.get(ancestor_url).json()
        return ancestor["title"]

def getAoDates(ao):
    if ao.get("dates"):
        # check for structured date field, return date as YYYY-YYYY
        if ao.get("dates")[0].get("begin"):
            return ao.get("dates")[0].get("begin", "") + "-" + ao.get("dates")[0].get("end", ao.get("dates")[0].get("begin", ""))
        # if there's no structured date, get date expression
        else:
            if ao.get("dates")[0].get("expression") == "n.d." or ao.get("dates")[0].get("expression") == "undated" or ao.get("dates")[0].get("expression") == "Undated":
                return ""
            elif len(ao.get("dates")[0].get("expression")) == 4:
                return ao.get("dates")[0].get("expression") + "-" + ao.get("dates")[0].get("expression")
            else:
                return ao.get("dates")[0].get("expression")

def getAoLevel(ao):
    # get level of description
    return ao.get("level")

def getAccessRestriction(ao):
    # iterate through archival object's notes, check for conditions governing access, return note
    if ao.get("notes"):
        for n in ao.get("notes"):
            if n.get("type") == "accessrestrict":
                return n.get("subnotes")[0].get("content").replace('\n', ' ') # replace line break with space

def getUseRestriction(ao):
    # iterate through archival object's notes, check for conditions governing use, return note
    if ao.get("notes"):
        for n in ao.get("notes"):
            if n.get("type") == "userestrict":
                return n.get("subnotes")[0].get("content").replace('\n', ' ') # replace line break with space

def getCreator(ao):
    # check whether there are agents linked to the resource or object
    if ao.get("linked_agents"):
        # create list to add each creator to
        creatorList = []
        # iterate through linked agents, check that their relationship to the record is as "creator" (not "subject")
        for la in ao["linked_agents"]:
            if la["role"] == "creator":
                # add each cretor to the creator list
                creator = client.get(la["ref"]).json()
                creatorList.append(creator.get("title"))
        # return creator list in pretty formatting
        return "; ".join(creatorList)
    else:
        return ""

def getAncestor(ao):
#    print("number of ancestors: " + str(len(ao["ancestors"])))
    # if archival object has a title, iterate through ancestors, return first ancestor that is not a resource
    if ao.get("title"):
        for a in ao.get("ancestors"):
            ancestor_url = a["ref"]
            ancestor = client.get(ancestor_url).json()
            if ancestor.get("jsonmodel_type") == "archival_object":
                return(ancestor)
    else:
        # if archival object does not have a title, start one ancestor up, then iterate through ancestors, return first ancestor that is not a resource
        ancestor_url = ao.get("ancestors")[0].get("ref")
        ao = client.get(ancestor_url).json()
        for a in ao.get("ancestors"):
            ancestor_url = a.get("ref")
            ancestor = client.get(ancestor_url).json()
            if ancestor.get("jsonmodel_type") == "archival_object":
                return(ancestor)

def getResource(ao):
    return client.get(ao["resource"]["ref"]).json()

def makeRow(ao,refid):
    row = []
    row.append(refid)
    row.append(getAoTitle(ao).replace('\n', ' '))
    row.append(getAoDates(ao))
    row.append(getAoLevel(ao))
    row.append(getAccessRestriction(ao))
#    row.append(getUseRestriction(ao))
    if getAncestor(ao):
        ancestor = getAncestor(ao)
        row.append(getAoTitle(ancestor).replace('\n', ' '))
        row.append(getAoLevel(ancestor))
        row.append(getAoDates(ancestor))
        row.append(getAccessRestriction(ancestor))
#        row.append(getUseRestriction(ancestor))
    else:
        row.append("")
        row.append("")
        row.append("")
        row.append("")
#        row.append("")
    resource = getResource(ao)
    row.append(resource["title"] + " (" + resource["id_0"] + ")")
    row.append(getAoDates(resource))
    row.append(getCreator(resource))
    row.append(getAccessRestriction(resource))
    row.append(getUseRestriction(resource))
    writer.writerow(row)
    print()

def makeSpreadsheet(filelist):
    total = len(filelist)
    count = 0
    for f in filelist:
        f = f.replace('\n', '')
        count += 1
        makeRow(getAo(f),f)
        print('Row added! - ' + str(count) + "/" + str(total))

# enter aspace login info
config = configparser.ConfigParser()
config.read('local_settings.cfg')
baseurl= config.get('ArchivesSpace', 'baseURL')
user = input('ArchivesSpace username: ')
pw = getpass.getpass('ArchivesSpace password:')

# start aspace session
client = ASnakeClient(baseurl=baseurl,username=user,password=pw)
print("Logging into ArchivesSpace...")
client.authorize()

# create spreadsheet
spreadsheet = open("findOnDemand.csv", "w")
writer = csv.writer(spreadsheet)
columnHeadings = ["RefId", "Title", "Component Dates", "Component Level", "Component Access Restricton", "Ancestor", "Ancestor Level", "Ancestor Dates", "Ancestor Access Restriction", "Parent Resource", "Resource Dates", "Resource Creator(s)", "Resource Access Restriction", "Resource Use Restriction"]
writer.writerow(columnHeadings)

fileList = open("refids.txt").readlines()
makeSpreadsheet(fileList)
print('\a')
