#!/usr/bin/env python

# used for digital media transfers
# creates a CSV file matching the filename to the Archivespace ref_id included in the /metadata directory of an Archivematica transfer

import glob, os, csv
from os import path

# get dmID and Archivespace Ref ID
# find transfer directory - expects directory name to follow the convention Desktop/FA/dmID/
findingaid = input('Enter the FA number, include FA: ')
dmID = input('Enter the digital media id: ')
objects_directory = path.join(findingaid, dmID, 'objects')
metadata_directory = path.join('Desktop', findingaid, dmID, 'metadata')
#get Archivespace ref_id
global asrefid
asrefid = input("Enter the Archivespace Ref ID: ")
#print(os.getcwd())
os.chdir(objects_directory)
#print(os.getcwd())
filenames = sorted(glob.glob('**', recursive=True))

def makeRow(filename, asrefid):
    row = []
    row.append(filename)
    row.append(asrefid)
    return row

def makeSpreadsheet(filenames, asrefid):
    os.chdir('..')
    #print(os.getcwd())
    with open(path.join('metadata', 'archivesspacids.csv'), 'w') as spreadsheet:
        writer = csv.writer(spreadsheet)
    #for each file, write as_refid rows
        for f in filenames:
            filename = 'objects/' + f
            writer.writerow(makeRow(filename, asrefid))

makeSpreadsheet(filenames, asrefid)

print("Creating csv...")
print("Done!")
print("The spreadsheet is located in: ")
print(metadata_directory + "/archivesspacids.csv")
