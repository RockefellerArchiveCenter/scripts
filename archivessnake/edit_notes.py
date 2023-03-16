#!/usr/bin/env python3

import argparse
from configparser import ConfigParser
import csv
import os
import time

from asnake.aspace import ASpace
from asnake.utils import walk_tree
#from fuzzywuzzy import fuzz
from rapidfuzz import fuzz

AS_REPOSITORY = 2
OUTPUT_FILENAME = "out.csv"
NOTE_TYPE_CHOICES = ["bioghist", "accessrestrict", "odd", "abstract", "arrangement", "userestrict", "fileplan", "acqinfo", "langmaterial", "physdesc", "prefercite", "processinfo", "relatedmaterial", "separatedmaterial"]
ACTION_CHOICES = ["modify", "delete"]
LEVEL = ["collection", "file", "series", "item", "all"]
CONFIDENCE_RATIO = 97

def process_tree(args, resource_id):
    """Iterates through a given collection, file, or series provided by user input. Finds note content that matches user input and then deletes or modifies relevant notes according to user preference.  """
    for record in walk_tree(resource_id, client):
        updated = False
        if args.level in [record['level'], "all"]:
            notes = client.get(record['notes']).json()
            for idx, note in reversed(list(enumerate(notes))):
                if note['type'] == args.note_type:
                    for subnote in note.get(['subnotes']):
                        content = subnote['content']
                        if contains_match(content, args.search_string):
                            if args.action == "delete":
                                del notes[idx]
                                print("{} note deleted from object {}".format(
                                    args.note_type, record['uri']))
                            if args.action == "modify":
                                print("{} note was originally {} and was changed to {} in object {}".format(
                                    args.note_type, content, args.replace_string, record['uri']))
                                subnote['content'] = args.replace_string
                            log_to_spreadsheet(record)
                            updated = True
            if updated:
                save_record(record['uri'], record.json())

def contains_match(content, search_string):
    """Returns True if user-provided note input matches the corresponding note within a given ratio (CONFIDENCE_RATIO)."""
    ratio = fuzz.token_sort_ratio(content.lower(), search_string.lower())
    return True if ratio > CONFIDENCE_RATIO else False


def save_record(record, data):
    """Posts modifications/deletions to ArchivesSpace"""
    updated = client.post(record['uri'], json=data)
    updated.raise_for_status()


def log_to_spreadsheet(archival_object, resource_id, record):
    """Logs top container identifier information of changed archival objects to spreadsheet"""
    for instance in archival_object['instances']:
        top_container = instance.sub_container.top_container
        container = "{} {}".format(
            top_container.type.capitalize(), top_container.indicator)
        writer.writerow([resource_id['title'], resource_id['id_0'], record['uri'], record['ref_id'], record['title'], container])


def create_spreadsheet(column_headings):
    """Creates spreadsheet that logs top container information of changed archival objects"""
    writer.writerow(column_headings)

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("note_type", choices=NOTE_TYPE_CHOICES, help="The type of note within a finding aid you wish to modify or delete (ex. bioghist)")
    parser.add_argument("action", choices=ACTION_CHOICES, help="The action you wish to perform against matched notes")
    parser.add_argument("resource_id", type=int, help="The identifier of the resource record in which you want to search. Found in the URL.")
    parser.add_argument("search_string", help="A string to be matched against in resource record notes.")
    parser.add_argument("level", choices=LEVEL, help="The level within the resource hierarchy you would like to change (collection, series, file, item, or all).")
    parser.add_argument("-r", "--replace_string", help="The new note content to replace the old note content. (Only relevant if you are modifying note(s))")
    return parser

def main(client, writer):
    """Main function, which is run when this script is executed"""
    start_time = time.time()
    parser = get_parser()
    args = parser.parse_args()
    create_spreadsheet(["Collection Title", "Finding Aid Number", "URI", "Ref ID", "Object Title", "Box Number"])
    process_tree(args, client.repositories(AS_REPOSITORY).resources(args.resource_id))
    elapsed_time = time.time() - start_time
    print("Time Elapsed: " + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))

if __name__ == "__main__":
    client = ASpace().client
    spreadsheet_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), OUTPUT_FILENAME)
    writer = csv.writer(open(spreadsheet_path, "w"))
    main(client, writer)
