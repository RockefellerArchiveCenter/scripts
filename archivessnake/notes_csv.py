##!/usr/bin/env python3

import argparse
from configparser import ConfigParser
import csv
import os
import time

from asnake.aspace import ASpace
from asnake.utils import walk_tree

config = ConfigParser()
config.read("local_settings.cfg")

client = ASpace(baseurl=config.get('ArchivesSpace', 'baseURL'), username=config.get('ArchivesSpace', 'user'), password=config.get('ArchivesSpace', 'password')).client
spreadsheet_path = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), config.get(
        "Destinations", "filename"))
writer = csv.writer(open(spreadsheet_path, "w"))

NOTE_TYPE_CHOICES = ["bioghist", "accessrestrict", "odd", "abstract", "arrangement", "userestrict", "fileplan", "acqinfo", "langmaterial", "physdesc", "phystech", "prefercite", "processinfo", "relatedmaterial", "scopecontent", "separatedmaterial"]

def process_tree(args, resource_id):
    """Iterates through a collection with note type and resource ID provided by user input. Writes Collection Title, Finding Aid Number, URI, Object Title, Date, Note Content, Container ID/Box Number, Folder, and Location to a csv file."""
    for record in walk_tree(resource_id, client):
        for note in record['notes']:
            if note['type'] == args.note_type:
                    for subnote in note['subnotes']:
                        content = subnote['content']
                        try:
                            expression = record['dates'][0]['expression']
                        except (KeyError, IndexError):
                            expression = "undated"
                        for instance in record['instances']:
                            sub_container = instance['sub_container']
                            top_container = aspace.client.get(instance['sub_container']['top_container']['ref']).json()
                            try:
                                container = "{} {}".format(
                                top_container['type'].capitalize(), top_container['indicator'])
                            except KeyError:
                                container = "None"
                            try:
                                container_2 = "{} {}".format(sub_container['type_2'].capitalize(), sub_container['indicator_2'])
                            except KeyError:
                                container_2 = "None"
                            location = ""
                            for loc in top_container['container_locations']:
                                try:
                                    l = aspace.client.get(loc['ref']).json()
                                    location = l['title']
                                except KeyError:
                                    location = "None"
                            writer.writerow([resource_id['title'], resource_id['id_0'], record['uri'], record['title'], record['level'], expression, content, container, container_2, location])

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("note_type", choices=NOTE_TYPE_CHOICES, help="The type of note within a finding aid. For example: accessrestrict.")
    parser.add_argument("resource_id", type=int, help="The identifier of the resource record in which you want to write info to a csv. Found in the URL.")
    return parser

def main(aspace, writer):
     #"""Main function, which is run when this script is executed"""
    start_time = time.time()
    parser = get_parser()
    args = parser.parse_args()
    writer.writerow(["Collection Title", "Finding Aid Number", "URI", "Object Title", "Level", "Date", "Note Content", "Container ID/Box Number", "Folder", "Location"])
    process_tree(args, client.get(f'/repositories/2/resources/{(args.resource_id)}').json())
    elapsed_time = time.time() - start_time
    print("Time Elapsed: " + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))


if __name__ == "__main__":
    main(aspace, writer)
