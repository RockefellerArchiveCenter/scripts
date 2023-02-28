##!/usr/bin/env python3

import argparse
import csv
import os
import time

from asnake.aspace import ASpace

FILENAME = "out.csv"

NOTE_TYPE_CHOICES = ["bioghist", "accessrestrict", "odd", "abstract", "arrangement", "userestrict", "fileplan", "acqinfo", "langmaterial", "physdesc", "prefercite", "processinfo", "relatedmaterial", "separatedmaterial"]
LEVEL = ["collection", "file", "series", "item", "all"]
CONFIDENCE_RATIO = 97

def process_tree(note_type, resource):
    """Iterates through a given collection, file, or series for note type provided by user input. Finds and prints note content."""
    for record in resource.tree.walk:
        for note in record.notes:
            if note.type == args.note_type:
                for subnote in note.subnotes:
                    content = subnote.content
                    print(content)

def main(note_type, resource_id):
    """Main function, which is run when this script is executed"""
    start_time = time.time()
    parser = get_parser()
    aspace = ASpace()
    process_tree(note_type, aspace.repositories(2).resources(resource_id))
    elapsed_time = time.time() - start_time
    print("Time Elapsed: " + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("note_type", choices=NOTE_TYPE_CHOICES, help="The type of note within a finding aid you wish to print content from. For example: accessrestrict.")
    parser.add_argument("resource_id", type=int, help="The identifier of the resource record in which you want to print note content from. Found in the URL.")
    args = parser.parse_args()
    main(note_type, resource_id)
