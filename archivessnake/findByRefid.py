#!/usr/bin/env python3

import json
import csv
import getpass
import configparser
from asnake.client import ASnakeClient

def get_ao(refid):
    # use find_by_id endpoint
    url = 'repositories/2/find_by_id/archival_objects?ref_id[]=' + refid
    ao = client.get(url).json()
    # get archival object as json
    ao_ref = ao.get("archival_objects")[0].get("ref")
    ao = client.get(ao_ref).json()
    return ao

def get_title(ao):
    # check if archival object has a title
    if ao.get("title"):
        return ao.get("title")
    # if there's no title, use the title of its immediate ancestor
    else:
        ancestor_url = ao.get("ancestors")[0].get("ref")
        ancestor = client.get(ancestor_url).json()
        return ancestor["title"]

def is_year(date, x, y):
    if date[x:y].isdigit() and int(date[x:y]) >= 1800 and int(date[x:y]) <= 2010:
        return True
    else:
        return False

def find_year(date):
     # takes a string, and finds a 4 digit string matching years likely in our collections, working backwards from end of string; checks last four characters before looping
    if len(date) >= 4:
        if is_year(date, -4, None):
            return date[-4:]
        else:
            x=-5
            y=-1
            for r in range(len(date)):
                if is_year(date, x, y):
                    return date[x:y]
                    break
                else:
                    x += -1
                    y += -1

def check_undated(ao):
    # ignore date expressions that only consist of some form of undated; will return false for a date expression like "1940, undated"
    if ao.get("dates")[0].get("expression") not in ["n.d.", "undated", "Undated"]:
        return True
    else:
        return False

def find_bulk_dates(ao):
    # check whether there are multiple dates; if there are, use information from the bulk date
    if ao.get("dates"):
        if len(ao.get("dates")) >= 2:
            for bulk in [d for d in ao.get('dates') if d.get('date_type') in ['bulk']]:
                if bulk.get("begin"):
                    return bulk.get("end", bulk.get("begin"))
                else:
                    return bulk.get("expression")

def find_ancestor_date(ao):
    # get the first ancestor of a component (parent)
    a = ao.get("ancestors")[0]
    ancestor = client.get(a.get("ref")).json()
    # check whether parent is an archival object, as opposed to a resource
    if ancestor.get("jsonmodel_type") == "archival_object" and ancestor.get("dates"):
        if find_bulk_dates(ancestor):
            return find_bulk_dates(ancestor)
        else:
            d = ancestor.get("dates")[0]
            if d.get("begin"):
                return d.get("end", d.get("begin"))
            # if there's no structured date, get date expression
            else:
                return find_year(d.get("expression"))

def get_end_date(ao):
    # uses either structured date or date expression to get end year
    if ao.get("dates"):
        if find_bulk_dates(ao):
            return find_bulk_dates(ao)
        else:
            # check for structured date field, return date as YYYY-YYYY
            if ao.get("dates")[0].get("begin"):
                return find_year(ao.get("dates")[0].get("end", ao.get("dates")[0].get("begin", "")))
            # if there's no structured date, get date expression
            else:
                if check_undated(ao):
                    if len(ao.get("dates")[0].get("expression")) == 4:
                        return ao.get("dates")[0].get("expression")
                    else:
                        return find_year(ao.get("dates")[0].get("expression"))
                elif get_ancestor(ao):
                    find_ancestor_date(ao)
    elif get_ancestor(ao):
        find_ancestor_date(ao)
                        
def get_start_date(ao):
    # uses structured date to get begin year
    if ao.get("dates"):
        # check for structured date field, return date as YYYY-YYYY
        if ao.get("dates")[0].get("begin"):
            return find_year(ao.get("dates")[0].get("begin", ""))

def get_ao_level(ao):
    # get level of description
    return ao.get("level")

def get_specific_note(ao, noteType):
    if ao.get("notes"):
        for n in ao.get("notes"):
            if n.get("type") == noteType: #accessrestrict, userestrict
                return n.get("subnotes")[0].get("content").strip().replace('\n', ' ') # replace line break with space

def get_ao_notes(ao):
    # get note type for each note, append to list
    if ao.get("notes"):
        note_list = []
        for n in ao.get("notes"):
            if n.get("type") in ["bioghist", "scopecontent", "relatedmaterial", "separatedmaterial", "phystech", "processinfo", "otherfindaid", "originalsloc", "fileplan", "arrangement"]:
                if n.get("jsonmodel_type") not in ["note_definedlist"]:
                    note_list.append(n.get("subnotes")[0].get("content").replace('\n', ' ').strip())
        return " | ".join(note_list)
    else:
        return ""

def get_parent_ancestor(ao):
    if len(ao.get("ancestors")) >= 2:
        x = len(ao.get("ancestors")) - 2
        ancestor_url = ao.get("ancestors")[x].get("ref")
        ancestor = client.get(ancestor_url).json()
        return(ancestor)

def get_ancestor(ao):
    # first check whether a component has a title; if it does not, the title of its parent is used in the component title column; so for the purposes of this "ancestor", it fetches the parent of the component that has a title
    if ao.get("title"):
        if ao.get("ancestors"):
            # check whether a component has at least two ancestors; if there is only one ancestor, that means its parent is a resource
            return get_parent_ancestor(ao)
    else:
        ancestor_url = ao.get("ancestors")[0].get("ref")
        ao = client.get(ancestor_url).json()
        if ao.get("ancestors"):
            return get_parent_ancestor(ao)

def get_resource(ao):
    return client.get(ao["resource"]["ref"]).json()
    
def find_best_component_date(ao):
    if get_end_date(ao):
        return get_end_date(ao)
    elif get_end_date(get_resource(ao)):
        if int(get_end_date(get_resource(ao))) <= 1960:
            return get_end_date(get_resource(ao))

def make_row(ao,refid):
    row = []
    row.append(refid)
    row.append(get_title(ao).strip())
    row.append(find_best_component_date(ao))
    if get_ancestor(ao):
        ancestor = get_ancestor(ao)
        row.append(get_title(ancestor).strip() + " (" + get_ao_level(ancestor) + ")")
    else:
        row.append("")
    resource = get_resource(ao)
    resource_title = resource["title"]
    parent_collection = resource_title.split(', ')[0]
    row.append(parent_collection)
    rest_of_fA = resource_title[(len(parent_collection) + 2):]
    row.append(rest_of_fA.strip())
    row.append(resource["id_0"])
    row.append(get_start_date(resource))
    writer.writerow(row)

def make_spreadsheet(filelist):
    total = len(filelist)
    print('Starting - ' + str(total) + ' total rows')
    count = 0
    for f in filelist:
        f = f.replace('\n', '') # account for new line in text file
        count += 1
        make_row(get_ao(f),f)
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
spreadsheet = open("find_on_demand.csv", "w")
writer = csv.writer(spreadsheet)
column_headings = ["Ref_id", "Title", "Component End Year", "Ancestor", "Parent Collection", "Remainder of Finding Aid Title", "Resource ID", "Resource Start Year"]
writer.writerow(columnHeadings)

def createFileList():
    print("Removing refids to ignore...")
    originalList = open("refids.txt").readlines()
    ignoreList = open("ignorelist.txt").readlines()
    for i in ignoreList:
        if i in originalList:
            originalList.remove(i)
    return originalList

make_spreadsheet(createFileList())
print('\a')
