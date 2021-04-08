#!/usr/bin/env python3

from configparser import ConfigParser
from os.path import join

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
    file_uri = join("http://storage.rockarch.org/",
                    "{}-{}.pdf".format(dip_uuid, title))
    data = '{ "jsonmodel_type":"digital_object", "is_slug_auto":true, "file_versions":[{ "jsonmodel_type":"file_version", "is_representative":false, "file_uri":"{}", "xlink_actuate_attribute":"onRequest", "xlink_show_attribute":"new", "file_format_name":"pdf", "file_format_version":"Generic PDF", "publish":true}], "restrictions":false, "notes":[{"content": ["{}"], "jsonmodel_type": "note_digital_object", "type": "originalsloc","publish": false}],  "title":"{}", "digital_object_id": "{}"}'.format(file_uri, aip_uuid, title, dip_uuid)
    r = aspace.client.post(dao_url, data=data)
    if r.status_code != 200:
        raise Exception("Could not post {}: {}".format(
            title, r.json().get('error')))
    else:
        return title, dip_uuid


if __name__ == "__main__":
    main()
