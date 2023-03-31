#!/usr/bin/env python3

import argparse
import csv
import os
import time

from asnake.aspace import ASpace
from asnake.utils import walk_tree, text_in_note

OUTPUT_FILENAME = "out.csv"
NOTE_TYPE_CHOICES = ["bioghist", "accessrestrict", "odd", "abstract", "arrangement", "userestrict", "fileplan", "acqinfo", "langmaterial", "physdesc", "prefercite", "processinfo", "relatedmaterial", "separatedmaterial"]
ACTION_CHOICES = ["modify", "delete"]
LEVEL = ["collection", "file", "series", "item", "all"]
CONFIDENCE_RATIO = 97
                  
def process_record(record, level, note_type, action, search_string, replace_string):
    """Deletes or modifies relevant notes according to user preference"""
    updated = False
    if level in [record['level'], "all"]:
        notes = record['notes']
        for idx, note in reversed(list(enumerate(notes))):
            if note['type'] == note_type:
                for subnote in note.get('subnotes', []):
                    content = subnote['content']
                    if text_in_note(content, search_string, CONFIDENCE_RATIO):
                        updated = True
                        if action == "delete":
                            del notes[idx]
                            print("{} note {} deleted from object {}".format(
                                note_type, search_string, record['uri']))
                        if action == "modify":
                            print("{} note was originally {} and was changed to {} in object {}".format(
                                note_type, content, replace_string, record['uri']))
                            subnote['content'] = replace_string
    return (record, updated)

def save_record(client, uri, data):
    """Posts modifications/deletions to ArchivesSpace"""
    updated = client.post(uri, json=data)
    updated.raise_for_status()

def get_container(record, client):
    """Gets container data."""
    if record['instances']:
        for instance in record.get('instances', []):
            top_container = client.get(instance['sub_container']['top_container']['ref']).json()
            container = "{} {}".format(
            top_container['type'].capitalize(), top_container['indicator'])
    else: 
        container = "None"
    return container

def main(note_type, action, resource_id, search_string, level, replace_string):
    """Main function, which is run when this script is executed"""
    start_time = time.time()
    client = ASpace().client

    spreadsheet_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), OUTPUT_FILENAME)
    print(spreadsheet_path)
    with open(spreadsheet_path, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Collection Title", "Finding Aid Number", "URI", "Ref ID", "Object Title", "Box Number"])
        resource = client.get(f'/repositories/2/resources/{(resource_id)}').json()
        for record in walk_tree(resource, client):
            processed_record, updated = process_record(record, level, note_type, action, search_string, replace_string)
            if updated:
                container = get_container(record, client)
                writer.writerow([resource['title'], resource['id_0'], record['uri'], record['ref_id'], record.get('title'), container])
                save_record(client, record.uri, processed_record)
    
    elapsed_time = time.time() - start_time
    print("Time Elapsed: " + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("note_type", choices=NOTE_TYPE_CHOICES, help="The type of note within a finding aid you wish to modify or delete (ex. bioghist)")
    parser.add_argument("action", choices=ACTION_CHOICES, help="The action you wish to perform against matched notes")
    parser.add_argument("resource_id", type=int, help="The identifier of the resource record in which you want to search. Found in the URL.")
    parser.add_argument("search_string", help="A string to be matched against in resource record notes.")
    parser.add_argument("level", choices=LEVEL, help="The level within the resource hierarchy you would like to change (collection, series, file, item, or all).")
    parser.add_argument("-r", "--replace_string", help="The new note content to replace the old note content. (Only relevant if you are modifying note(s))")
    args = parser.parse_args()
    main(args.note_type, args.action, args.resource_id, args.search_string, args.level, args.replace_string)
