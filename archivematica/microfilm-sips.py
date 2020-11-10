# Prep digitized microfilm files for ingest into Archivematica

import argparse
import os
import re
from csv import writer
from datetime import datetime
from shutil import copy2
from time import time

#Create new folder and define name of new folder (probably use txt file that list folders like RFOD script)#
folder = ["Folder 1", "Folder 2", "Folder 3"]

# Create new folders within each folder


def makeSipDirectory(topDirectory, folder):
    print("Making SIP directory...")
    microfilmfolder = "sip_" + folder
    os.mkdir(os.path.join(topDirectory, microfilmfolder))
    targetDirectory = os.path.join(topDirectory, microfilmfolder)
    os.mkdir(os.path.join(targetDirectory, "logs"))
    os.mkdir(os.path.join(targetDirectory, "metadata"))
    os.mkdir(os.path.join(targetDirectory, "objects"))
    objectsDirectory = os.path.join(targetDirectory, "objects")
    os.mkdir(os.path.join(objectsDirectory, "access"))

# Copy preservation files in folder


def copyFiles(sourceMaster, destination):
    print("Copying files from " + source + " to " + destination + "...")
    for f in os.listdir(source):
        if not f[-5:] == "bs.db":
            copy2(os.path.join(source, f), destination)

# Copy access files in folder


def copyFiles(sourceAccess, destination):
    print("Copying files from " + source + " to " + destination + "...")
    for f in os.listdir(source):
        if not f[-5:] == "bs.db":
            copy2(os.path.join(source, f), destination)


def createAspaceCsv(metadata, access):
    print("Creating archivesspaceids.csv...")
    aspacecsv = os.path.join(metadata, 'archivesspaceids.csv')
    with open(aspacecsv, 'w', newline='') as csvfile:
        f = "objects/" + access
        writer(csvfile).writerow([f])


def getCopyrightEndDate(copyrightStartYear, copyrightTerm):
    copyrightEndYear = int(copyrightStartYear) + int(copyrightTerm)
    copyrightEndDate = str(copyrightEndYear) + "-12-31"
    return copyrightEndDate


def makeRow(filename, basis, status, determination_date, jurisdiction, start_date, end_date, note, grant_act, grant_restriction, grant_start_date, grant_end_date, grant_note):
    row = []
    row.append(filename)
    row.append(basis)
    row.append(status)
    row.append(determination_date)
    row.append(jurisdiction)
    row.append(start_date)
    row.append(end_date)
    # terms - for license basis #citation - for statute basis
    row.extend([''] * 2)
    row.append(note)
    row.append(grant_act)
    row.append(grant_restriction)
    row.append(grant_start_date)
    row.append(grant_end_date)
    row.append(grant_note)
    row.extend([''] * 3)  # doc_id_type #doc_id_value #doc_id_role
    return row


def makeCopyrightRow(filename, copyrightStartYear, copyrightTerm):
    determination_date = datetime.now().strftime("%Y-%m-%d")
    start_date = copyrightStartYear + "-01-01"
    end_date = getCopyrightEndDate(copyrightStartYear, copyrightTerm)
    note = 'Work for hire - copyright term ' + copyrightTerm + \
        ' years from date of creation. Copyright held by the Rockefeller Foundation.'
    return makeRow(filename, 'copyright', 'copyrighted', determination_date, 'us', start_date, end_date, note, 'publish', 'allow', '2019-01-01', 'open', '')


def makePolicyRow(filename, microfilm):
    if microfilm in ['Rockefeller Sanitary Commission microfilm', 'Bureau of Social Hygiene microfilm', 'LSRM microfilm']:
        note = "Rockefeller Foundation records are open after 20 years from creation."
    return makeRow(filename, 'policy', '', '', '', '1974-01-01', 'open', note, 'disseminate', 'allow', '2019-01-01', 'open', '')


def createRightsCsv(objectsDirectory, metadataDirectory, officer):
    filenames = os.listdir(objectsDirectory)
    with open(os.path.join(metadataDirectory, 'rights.csv'), 'w', newline='') as spreadsheet:
        column_headings = ["file", "basis", "status", "determination_date", "jurisdiction", "start_date", "end_date", "terms", "citation", "note",
                           "grant_act", "grant_restriction", "grant_start_date", "grant_end_date", "grant_note", "doc_id_type", "doc_id_value", "doc_id_role"]
        writer(spreadsheet).writerow(column_headings)
        # for each file, write copyright and donor rows
        for f in filenames:
            if f not in ['access', 'service', '.DS_Store', 'Thumbs.db']:
                filename = "objects/" + f
                writer(spreadsheet).writerow(
                    makeCopyrightRow(filename, findDate(f), "120"))
                writer(spreadsheet).writerow(makePolicyRow(filename, officer))
    print('Done!')


folder = open(args.folder).readlines()
for r in folder:
    print("Starting " + r + "...")
    sourceMaster = os.path.join(args.source_directory, r, "Master")
    sourceAccess = os.path.join(args.source_directory, r, "Service Edited")
#  create Archivematica SIP directory and subdirectories
    makeSipDirectory(args.sip_directory, r)
    sipDirectory = os.path.join(args.sip_directory, "sip_" + r)
    metadataDirectory = os.path.join(sipDirectory, "metadata")
    objectsDirectory = os.path.join(sipDirectory, "objects")
    accessDirectory = os.path.join(objectsDirectory, "access")
    copyFiles(sourceMaster, objectsDirectory)
    copyFiles(sourceAccess, accessDirectory)
