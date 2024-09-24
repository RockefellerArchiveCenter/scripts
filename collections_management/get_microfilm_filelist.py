#!/usr/bin/env python

from asnake.aspace import ASpace

aspace = ASpace()
repo = aspace.repositories(2)

output_file = "output_filename.tsv"

resource_id = 12345


def is_year(date, x, y):
    '''
    date (str): string to check for a 4 digit year
    x (int): starting index value
    y (int): ending index value
    '''
    if date[x:y].isdigit() and int(
            date[x:y]) >= 1800 and int(date[x:y]) <= 2010:
        return True
    else:
        return False


def find_year(date):
    '''takes a string, and finds a 4 digit string matching years likely in our
    collections, working backwards from end of string; checks last four
    characters before looping'''
    if len(date) >= 4:
        if is_year(date, -4, None):
            return date[-4:]
        else:
            x = -5
            y = -1
            for r in range(len(date)):
                if is_year(date, x, y):
                    return date[x:y]
                    break
                else:
                    x += -1
                    y += -1


def get_end_date(ao, default_date):
    # uses either structured date or date expression to get end year
    if ao.get("dates"):
        # check for structured date field, return date as YYYY-YYYY
        if ao.get("dates")[0].get("begin"):
            return find_year(
                ao.get("dates")[0].get(
                    "end", ao.get("dates")[0].get(
                        "begin", "")))
        else:
            if len(ao.get("dates")[0].get("expression")) == 4:
                return ao.get("dates")[0].get("expression")
            else:
                return find_year(ao.get("dates")[0].get("expression"))
    else:
        return default_date


# create empty list to append uris to
list_of_uris = []

for record in repo.resources(resource_id).tree.walk:
    # traverse tree of resource record, use level to skip series
    if record.level == "file":
        list_of_uris.append(record.uri)

f = open(output_file, "a")


for uri in list_of_uris:
    obj = aspace.client.get(uri, params={"resolve": ["top_container"]})
    item_json = obj.json()
    if item_json.get("instances"):
        for i in item_json.get("instances"):
            if i.get("instance_type") != "digital_object":
                subcontainer = i.get('sub_container')
                if subcontainer.get("type_2") == "folder":
                    folder_number = "{} {}".format(subcontainer.get(
                        'type_2'), subcontainer.get('indicator_2'))
                top_container = subcontainer.get(
                    "top_container").get("_resolved")
                if top_container.get("type") == "box":
                    f.write(
                        "{}\t{} {}, {}\t{}\t{}\n".format(
                            item_json.get("title"),
                            top_container.get("type").capitalize(),
                            top_container.get("indicator"),
                            folder_number,
                            get_end_date(item_json, "1940"),
                            item_json.get("ref_id")))

f.close()
