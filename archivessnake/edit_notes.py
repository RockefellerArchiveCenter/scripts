#!/usr/bin/env python3

import argparse
from configparser import ConfigParser
import csv
import os
import time

from asnake.aspace import ASpace
from fuzzywuzzy import fuzz

config = ConfigParser()
config.read("local_settings.cfg")

spreadsheet_path = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), config.get(
        "Destinations", "filename")
)

NOTE_TYPE_CHOICES = ["bioghist", "accessrestrict", "odd", "abstract", "arrangement", "userestrict", "fileplan", "acqinfo", "langmaterial", "physdesc", "prefercite", "processinfo", "relatedmaterial"]
ACTION_CHOICES = ["modify", "delete"]
LEVEL = ["collection", "file", "series"]
CONFIDENCE_RATIO = 97

def process_tree(args, resource):
    for record in resource.tree.walk:
        updated = False
        aojson = record.json()
        if record.level == args.level:
            notes = aojson.get("notes")
            for idx, note in reversed(list(enumerate(notes))):
                if note["type"] == args.note_type:
                    for subnote in note.get("subnotes"):
                        content = subnote["content"]
                        if contains_match(content, args.search_string):
                            if args.action == "delete":
                                del notes[idx]
                                print("{} note deleted from object {}".format(
                                    args.note_type, record.uri))
                            if args.action== "modify":
                                print("{} note was originally {} and was changed to {} in object {}".format(
                                    args.note_type, content, args.replace_content, record.uri))
                                content = args.replace_content
                            log_to_spreadsheet(record)
                            updated = True
            if updated:
                save_record(record.uri, aojson)


def contains_match(note_content, search_string):
    ratio = fuzz.token_sort_ratio(note_content.lower(), search_string.lower())
    return True if ratio > CONFIDENCE_RATIO else False


def save_record(uri, data):
    updated = aspace.client.post(uri, json=data)
    updated.raise_for_status()


def log_to_spreadsheet(archival_object):
    for instance in archival_object.instances:
        top_container = instance.sub_container.top_container
        container = "{} {}".format(
            top_container.type.capitalize(), top_container.indicator)
        writer.writerow([container, archival_object.uri])


def create_spreadsheet(column_headings):
    writer.writerow(column_headings)

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("note_type", choices=NOTE_TYPE_CHOICES, help="The type of note within a finding aid you wish to modify or delete (ex. bioghist)")
    parser.add_argument("action", choices=ACTION_CHOICES, help="The action you wish to perform against matched notes")
    parser.add_argument("resource_id", type=int, help="The identifier of the resource record in which you want to search. Found in the URL.")
    parser.add_argument("search_string", help="A string to be matched against in resource record notes.")
    parser.add_argument("level", choices=LEVEL, help="The level within the resource hierarchy you would like to change (collection, series, or file).")
    parser.add_argument("-r", "--replace_string", help="The new note content to replace the old note content. (Only relevant if you are modifying note(s))")
    return parser

def main():
    start_time = time.time()
    parser = get_parser()
    args = parser.parse_args()
    global aspace
    aspace = ASpace(
        baseurl=config.get("ArchivesSpace", "baseURL"),
        user=config.get("ArchivesSpace", "user"),
        password=config.get("ArchivesSpace", "password"),
    )
    global writer
    writer = csv.writer(open(spreadsheet_path, "w"))
    create_spreadsheet(["Box Number", "Archival Object URI"])
    process_tree(args, aspace.repositories(config.get(
        "ArchivesSpace", "repository")).resources(args.resource_id))
    elapsed_time = time.time() - start_time
    print("Time Elapsed: " + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))


if __name__ == "__main__":
    main()