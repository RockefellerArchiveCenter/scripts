#!/usr/bin/env python

import os
import json
import csv
from asnake.aspace import ASpace

def write_subject_csv(csvName, aspace):
    """Writes subject data to a csv"""
    fieldnames = ['URI', 'subject']
    with open(csvName, 'w', newline='') as outputFile:
        writer = csv.DictWriter(outputFile, fieldnames=fieldnames)
        writer.writeheader()
        get_subjects(writer, aspace)

def get_subjects(writer, aspace):
    """Gets subjects."""
    for object_type in ['subjects']:
        for object in getattr(aspace, object_type):
            if object.used_within_repositories == ['/repositories/2']:
                print("subjects/{}".format(object.uri.split('/')[-1]))
                writer.writerow({'URI': str(object.uri), 'subject': object.title})


if __name__ == "__main__":
    aspace = ASpace()
    csvName = "subjects.csv"
    write_subject_csv(csvName, aspace)
