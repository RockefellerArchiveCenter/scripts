#!/usr/bin/env python

import os
import json
import csv
from asnake.aspace import ASpace


aspace = ASpace()
repo = aspace.repositories(2)

###Writes subject data to a csv
def write_subject_csv(csvName):
    fieldnames = ['URI', 'subject']
    with open(csvName, 'w', newline='') as outputFile:
        writer = csv.DictWriter(outputFile, fieldnames=fieldnames)
        writer.writeheader()
        get_subjects(writer)

###Gets subjects
def get_subjects(writer):
    for object_type in ['subjects']:
        for object in getattr(aspace, object_type):
            if object.used_within_repositories == ['/repositories/2']:
                print("subjects/{}".format(object.uri.split('/')[-1]))
                writer.writerow({'URI': str(object.uri), 'subject': object.title})

csvName = "subjects.csv"
write_subject_csv(csvName)
