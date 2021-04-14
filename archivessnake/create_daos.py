#!/usr/bin/env python3

"""
Using DIP information from Archivematica, adds digital object to file-level children of a series in ArchivesSpace.

Expects an external pickle file that contains a list of dictionaries with the following information:
    current_full_path: full path to DIP (from Archivematica)
    related_packages: AIP URI (from Archivematica)
    uuid: DIP UUID (from Archivematica)
    box: parsed from current_full_path
    folder: parsed from current_full_path
"""

import argparse
import pickle
from configparser import ConfigParser
from os.path import join

import requests
from asnake.aspace import ASpace

# set up archivesspace client
config = ConfigParser()
config.read("local_settings.cfg")

# get token


def main():
    #"""Main function, which is run when this script is executed"""
    aspace = ASpace(baseurl=config.get("ArchivesSpace", "baseURL"), username=config.get(
        "ArchivesSpace", "username"), password=config.get("ArchivesSpace", "password"))
    dao_url = join(config.get("ArchivesSpace", "baseURL"),
                   "repositories/2/digital_objects")
    try:
        post_dao(dao_url, aspace_token, dip_uuid, title, aip_uuid)
    except Exception as e:
        print(e)


def post_dao(dao_url, aspace, dip_uuid, title, aip_uuid):
    """docstring for post_dao"""
    aspace_token = aspace.client.authorize()
    headers = {'X-ArchivesSpace-Session': aspace_token}
    file_uri = join("http://storage.rockarch.org/",
                    "{}-{}.pdf".format(dip_uuid, title))
    data = { "jsonmodel_type":"digital_object", "is_slug_auto":True, "file_versions":[{ "jsonmodel_type":"file_version", "is_representative":False, "file_uri":str(file_uri), "xlink_actuate_attribute":"onRequest", "xlink_show_attribute":"new", "file_format_name":"pdf", "file_format_version":"Generic PDF", "publish":True}], "restrictions":False, "notes":[{"jsonmodel_type": "note_digital_object", "content": [str(aip_uuid)], "type": "originalsloc","publish": False}],  "title":str(title), "digital_object_id": str(dip_uuid)}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    if r.status_code != 200:
        raise Exception("Could not post {}: {}".format(
            title, r.json().get('error')))
    else:
        return title, dip_uuid


if __name__ == "__main__":
    main()
