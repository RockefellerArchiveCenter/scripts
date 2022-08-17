##!/usr/bin/env python3

import argparse
from configparser import ConfigParser
import csv
import os
import time

from asnake.aspace import ASpace

config = ConfigParser()
config.read("local_settings.cfg")

aspace = ASpace(baseurl=config.get('ArchivesSpace', 'baseURL'), username=config.get('ArchivesSpace', 'user'), password=config.get('ArchivesSpace', 'password'))
spreadsheet_path = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), config.get(
        "Destinations", "filename"))
writer = csv.writer(open(spreadsheet_path, "w"))

NOTE_TYPE_CHOICES = ["bioghist", "accessrestrict", "odd", "abstract", "arrangement", "userestrict", "fileplan", "acqinfo", "langmaterial", "physdesc", "phystech", "prefercite", "processinfo", "relatedmaterial", "scopecontent", "separatedmaterial"]

def process_tree(args, resource):
    """Iterates through a collection with note type and resource ID provided by user input. Writes Collection Title, Finding Aid Number, URI, Object Title, Date, Note Content, Container ID/Box Number, Folder, and Location to a csv file."""
    for record in resource.tree.walk:
        for note in record.notes:
            if note.type == args.note_type:
                    for subnote in note.subnotes:
                        content = subnote.content
                        try:
                            expression = record.dates[0].expression
                        except (KeyError, IndexError):
                            expression = "undated"
                        for instance in record.instances:
                            sub_container = instance.sub_container
                            top_container = instance.sub_container.top_container
                            try:
                                container_2 = "{} {}".format(sub_container.type_2.capitalize(), sub_container.indicator_2)
                            except KeyError:
                                container_2 = None
                                writer.writerow([resource.title, resource.id_0, record.uri, record.title, expression, content, container, container_2, loc.title])
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
    writer.writerow(["Collection Title", "Finding Aid Number", "URI", "Object Title", "Date", "Note Content", "Container ID/Box Number", "Folder", "Location"])
    process_tree(args, aspace.repositories(config.get(
        "ArchivesSpace", "repository")).resources(args.resource_id))
    elapsed_time = time.time() - start_time
    print("Time Elapsed: " + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))


if __name__ == "__main__":
    main(aspace, writer)
