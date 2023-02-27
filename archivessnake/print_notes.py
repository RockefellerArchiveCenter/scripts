##!/usr/bin/env python3

import argparse
import csv
import os
import time

from asnake.aspace import ASpace

FILENAME = "out.csv"

aspace = ASpace()
spreadsheet_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), FILENAME)

NOTE_TYPE_CHOICES = ["bioghist", "accessrestrict", "odd", "abstract", "arrangement", "userestrict", "fileplan", "acqinfo", "langmaterial", "physdesc", "prefercite", "processinfo", "relatedmaterial", "separatedmaterial"]
LEVEL = ["collection", "file", "series", "item", "all"]
CONFIDENCE_RATIO = 97

def process_tree(args, resource):
    """Iterates through a given collection, file, or series for note type provided by user input. Finds and prints note content."""
    for record in resource.tree.walk:
        for note in record.notes:
            if note.type == args.note_type:
                for subnote in note.subnotes:
                    content = subnote.content
                    print(content)

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("note_type", choices=NOTE_TYPE_CHOICES, help="The type of note within a finding aid you wish to print content from. For example: accessrestrict.")
    parser.add_argument("resource_id", type=int, help="The identifier of the resource record in which you want to print note content from. Found in the URL.")
    parser.add_argument("level", choices=LEVEL, help="The level within the resource hierarchy you would like to print note content from (collection, series, file, item, or all).")
    return parser

def main():
     #"""Main function, which is run when this script is executed"""
    start_time = time.time()
    parser = get_parser()
    args = parser.parse_args()
    aspace = ASpace()
    process_tree(args, aspace.repositories(2).resources(args.resource_id))
    elapsed_time = time.time() - start_time
    print("Time Elapsed: " + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))


if __name__ == "__main__":
    main()
