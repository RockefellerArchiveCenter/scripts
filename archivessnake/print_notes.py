#!/usr/bin/env python3

import argparse
from configparser import ConfigParser
import csv
import os
import time

from asnake.aspace import ASpace
#from fuzzywuzzy import fuzz
from rapidfuzz import fuzz

config = ConfigParser()
config.read("local_settings.cfg")

spreadsheet_path = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), config.get(
        "Destinations", "filename")
)

NOTE_TYPE_CHOICES = ["bioghist", "accessrestrict", "odd", "abstract", "arrangement", "userestrict", "fileplan", "acqinfo", "langmaterial", "physdesc", "prefercite", "processinfo", "relatedmaterial", "separatedmaterial"]
LEVEL = ["collection", "file", "series", "item"]
CONFIDENCE_RATIO = 97

def process_tree(args, resource):
    """Iterates through a given collection, file, or series for note type provided by user input. Finds and prints note content."""
    for record in resource.tree.walk:
        aojson = record.json()
        if record.level == args.level or args.level == None:
            notes = aojson.get("notes")
            for idx, note in reversed(list(enumerate(notes))):
                if note["type"] == args.note_type:
                    for subnote in note.get("subnotes"):
                        content = subnote["content"]
                        print(content)

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("note_type", choices=NOTE_TYPE_CHOICES, help="The type of note within a finding aid you wish to print content from. For example: accessrestrict.")
    parser.add_argument("resource_id", type=int, help="The identifier of the resource record in which you want to print note content from. Found in the URL.")
    parser.add_argument("-l", "--level", choices=LEVEL, help="The level within the resource hierarchy you would like to print note content from (collection, series, file, or item).")
    return parser

def main():
     #"""Main function, which is run when this script is executed"""
    start_time = time.time()
    parser = get_parser()
    args = parser.parse_args()
    global aspace
    aspace = ASpace(
        baseurl=config.get("ArchivesSpace", "baseURL"),
        username=config.get("ArchivesSpace", "user"),
        password=config.get("ArchivesSpace", "password"),
    )
    process_tree(args, aspace.repositories(config.get(
        "ArchivesSpace", "repository")).resources(args.resource_id))
    elapsed_time = time.time() - start_time
    print("Time Elapsed: " + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))


if __name__ == "__main__":
    main()
