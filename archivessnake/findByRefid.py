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

def getTitle(ao):
    # check if archival object has a title
    if ao.get("title"):
        return ao.get("title")
    # if there's no title, use the title of its immediate ancestor
    else:
        ancestor_url = ao.get("ancestors")[0].get("ref")
        ancestor = client.get(ancestor_url).json()
        return ancestor["title"]

def findYear(date):
    if len(date) >= 4:
        if date[-4:].isdigit() and int(date[-4:]) >= 1850 and int(date[-4:]) <= 2020:
            year=date[-4:]
            return year
        else:
            x=-5
            y=-1
            for r in range(len(date)):
                if date[x:y].isdigit() and int(date[x:y]) >= 1850 and int(date[x:y]) <= 2020:
                    year=date[x:y]
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

def findBulkDates(ao):
    if ao.get("dates"):
        if len(ao.get("dates")) == 2:
            for d in ao.get("dates"):
                if d.get("date_type") in ["bulk"]:
                    if d.get("begin"):
                        return d.get("begin") + "-" + d.get("end", d.get("begin"))
                    # if there's no structured date, get date expression
                    else:
                        return d.get("expression")

def findAncestorDate(ao):
    a = ao.get("ancestors")[0]
    ancestor = client.get(a.get("ref")).json()
    if ancestor.get("jsonmodel_type") == "archival_object" and ancestor.get("dates"):
        findBulkDates(ancestor)
    elif ancestor.get("dates"):
        d = ancestor.get("dates")[0]
        if d.get("begin"):
            return d.get("end", d.get("begin"))
        # if there's no structured date, get date expression
        else:
            return findYear(d.get("expression"))

def getAoDates(ao):
    if ao.get("dates"):
        # check for structured date field, return date as YYYY-YYYY
        if ao.get("dates")[0].get("begin"):
            return findYear(ao.get("dates")[0].get("end", ao.get("dates")[0].get("begin", "")))
        # if there's no structured date, get date expression
        else:
            if checkUndated(ao):
                if len(ao.get("dates")[0].get("expression")) == 4:
                    return ao.get("dates")[0].get("expression")
                else:
                    return findYear(ao.get("dates")[0].get("expression"))
            elif getAncestor(ao):
                findAncestorDate(ao)
    elif getAncestor(ao):
        findAncestorDate(ao)
                        
def getAoLevel(ao):
    # get level of description
    return ao.get("level")

def getSpecificNote(ao, noteType):
    if ao.get("notes"):
        for n in ao.get("notes"):
            if n.get("type") == noteType: #accessrestrict, userestrict
                return n.get("subnotes")[0].get("content").strip().replace('\n', ' ') # replace line break with space

def getAoNotes(ao):
    # get note type for each note, append to list
    if ao.get("notes"):
        noteList = []
        for n in ao.get("notes"):
            if n.get("type") in ["bioghist", "scopecontent", "relatedmaterial", "separatedmaterial", "phystech", "processinfo", "otherfindaid", "originalsloc", "fileplan", "arrangement"]:
                if n.get("jsonmodel_type") not in ["note_definedlist"]:
                    noteList.append(n.get("subnotes")[0].get("content").replace('\n', ' ').strip())
        return " | ".join(noteList)
    else:
        return ""

def getAncestor(ao):
    if ao.get("title"):
        if ao.get("ancestors"):
            if len(ao.get("ancestors")) >= 2:
                x = len(ao.get("ancestors")) - 2
                ancestor_url = ao.get("ancestors")[x].get("ref")
                ancestor = client.get(ancestor_url).json()
                return(ancestor)
    else:
        ancestor_url = ao.get("ancestors")[0].get("ref")
        ao = client.get(ancestor_url).json()
        if ao.get("ancestors"):
            if len(ao.get("ancestors")) >= 2:
                x = len(ao.get("ancestors")) - 2
                ancestor_url = ao.get("ancestors")[x].get("ref")
                ancestor = client.get(ancestor_url).json()
                return(ancestor)

def getResource(ao):
    return client.get(ao["resource"]["ref"]).json()

def makeRow(ao,refid):
    row = []
    row.append(refid)
    row.append(getTitle(ao).strip())
    if getAoDates(ao):
        row.append(getAoDates(ao))
    elif getAoDates(getResource(ao)):
        if int(getAoDates(getResource(ao))) <= 1960:
            row.append(getAoDates(getResource(ao)))
        else:
            row.append("")
    else:
        row.append("")
    if getAncestor(ao):
        ancestor = getAncestor(ao)
        row.append(getTitle(ancestor).strip() + " (" + getAoLevel(ancestor) + ")")
    else:
        row.append("")
    resource = getResource(ao)
    resourceTitle = resource["title"]
    parentCollection = resourceTitle.split(', ')[0]
    row.append(parentCollection)
    restOfFA = resourceTitle[(len(parentCollection) + 2):]
    row.append(restOfFA.strip())
    row.append(resource["id_0"])
    row.append(getAoDates(resource))
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
columnHeadings = ["RefId", "Title", "Component Dates", "Ancestor", "Parent Collection", "Remainder of Finding Aid Title", "Resource ID", "Resource End Date"]
writer.writerow(columnHeadings)

fileList = open("refids.txt").readlines()
makeSpreadsheet(fileList)
print('\a')

