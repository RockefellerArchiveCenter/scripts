#!/usr/bin/env python3

import json
import csv
import getpass
import configparser
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

def findDate(date):
    if len(date) >= 4:
        if date[-4:].isdigit() and int(date[-4:]) >= 1850 and int(date[-4:]) <= 2020:
            year=date[-4:]
            return year
        else:
            print(date)
            x=-5
            y=-1
            for r in range(len(date)):
                if date[x:y].isdigit() and int(date[x:y]) >= 1850 and int(date[x:y]) <= 2020:
                    year=date[x:y]
                    print(year)
                    return year
                    break
                else:
                    x += -1
                    y += -1
                

def checkUndated(ao):
    if ao.get("dates")[0].get("expression") not in ["n.d.", "undated", "Undated"]:
        return True
    else:
        return False

def getAoDates(ao):
    if ao.get("dates"):
        # check for structured date field, return date as YYYY-YYYY
        if ao.get("dates")[0].get("begin"):
            return findDate(ao.get("dates")[0].get("end", ao.get("dates")[0].get("begin", "")))
        # if there's no structured date, get date expression
        else:
            if checkUndated(ao):
                if len(ao.get("dates")[0].get("expression")) == 4:
                    return ao.get("dates")[0].get("expression")
                else:
                    return findDate(ao.get("dates")[0].get("expression"))
    elif getAncestor(ao):
        # if the component does not have have dates, go to its ancestor archival object(s) and look for dates
        for a in ao.get("ancestors"):
            ancestor = client.get(a.get("ref")).json()
            if ancestor.get("jsonmodel_type") == "archival_object" and ancestor.get("dates"):
                if ancestor.get("dates")[0].get("begin"):
                    return findDate(ancestor.get("dates")[0].get("end", ancestor.get("dates")[0].get("begin", "")))
                    break
                # if there's no structured date, get date expression
                else:
                    if checkUndated(ancestor):
                        if len(ancestor.get("dates")[0].get("expression")) == 4:
                            return ancestor.get("dates")[0].get("expression")
                            break
                        else:
                            return findDate(ancestor.get("dates")[0].get("expression"))
                        
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

def getAoNotes(ao):
    # get note type for each note, append to list
    if ao.get("notes"):
        noteList = []
        for n in ao.get("notes"):
            if n.get("type") in ["bioghist", "scopecontent", "relatedmaterial", "separatedmaterial", "phystech"]:
                noteList.append(n.get("subnotes")[0].get("content").replace('\n', ' '))
        return " | ".join(noteList)
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
        if ao.get("ancestors"):
            for a in ao.get("ancestors"):
                ancestor_url = a.get("ref")
                ancestor = client.get(ancestor_url).json()
                if ancestor.get("jsonmodel_type") == "archival_object":
                    return(ancestor)
        else:
            ao.get("display_title")

def getResource(ao):
    return client.get(ao["resource"]["ref"]).json()

def makeRow(ao,refid):
    row = []
    row.append(refid)
    row.append(getAoTitle(ao).replace('\n', ' '))
    row.append(getAoDates(ao))
    row.append(getAccessRestriction(ao))
    row.append(getAoNotes(ao))
    if getAncestor(ao):
        ancestor = getAncestor(ao)
        row.append(getAoTitle(ancestor).replace('\n', ' ') + " (" + getAoLevel(ancestor) + ")")
        row.append(getAccessRestriction(ancestor))
        row.append(getAoNotes(ancestor))
    else:
        row.append("")
        row.append("")
        row.append("")
    resource = getResource(ao)
    row.append(resource["title"].split(', ')[0])
    row.append(resource["title"].strip(resource["title"].split(', ')[0] + ", "))
    row.append(resource["id_0"])
    row.append(getAoDates(resource))
    row.append(getAccessRestriction(resource))
    row.append(getUseRestriction(resource))
    writer.writerow(row)

def makeSpreadsheet(filelist):
    total = len(filelist)
    print('Starting - ' + str(total) + ' total rows')
    count = 0
    for f in filelist:
        f = f.replace('\n', '') # account for new line in text file
        count += 1
        makeRow(getAo(f),f)
        if not count % 25:
            print(str(count) + ' rows added')

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
columnHeadings = ["RefId", "Title", "Component Dates", "Component Access Restricton", "Component Notes", "Ancestor", "Ancestor Access Restriction", "Ancestor Notes", "Parent Collection", "Finding Aid Title", "Resource ID", "Resource Dates", "Resource Access Restriction", "Resource Use Restriction"]
writer.writerow(columnHeadings)

fileList = open("refids.txt").readlines()
makeSpreadsheet(fileList)
print('\a')

