#!/usr/bin/env python

import os, argparse, re
from csv import writer
from shutil import copy2
from time import time

def makeSipDirectory(topDirectory, officer):
    print("Making SIP directory...")
    officer = "sip_" + officer
    os.mkdir(os.path.join(topDirectory, officer))
    targetDirectory = os.path.join(topDirectory, officer)
    os.mkdir(os.path.join(targetDirectory, "logs"))
    os.mkdir(os.path.join(targetDirectory, "metadata"))
    os.mkdir(os.path.join(targetDirectory, "objects"))
    objectsDirectory = os.path.join(targetDirectory, "objects")
    os.mkdir(os.path.join(objectsDirectory, "access"))

def checkAccessPdf(directory):
    # check whether access files (i.e., files in /service_edited) are JPGs or a multipage-pdf
    if re.search(".pdf", " ".join(os.listdir(directory)), re.IGNORECASE):
        return True

def copyFiles(source, destination):
    print("Copying files from " + source + " to " + destination + "...")
    for f in os.listdir(source):
        if not f[-5:] == "bs.db":
            copy2(os.path.join(source, f), destination)
            if f[-7:-4] in ["_me", "_se"]:
                newName = f[:-7] + f[-4:]
                os.replace(os.path.join(destination, f), os.path.join(destination, newName))

                
def createAspaceCsv(metadata, access, objects):
    print("Creating archivesspaceids.csv...")
    aspacecsv = os.path.join(metadata, 'archivesspaceids.csv')
    filenames = []
    if checkAccessPdf(access):
        for a in os.listdir(access):
            filenames.append(a)
    else:
        for a in os.listdir(objects):
            filenames.append(a)
    with open(aspacecsv, 'w') as csvfile:
        for f in filenames:
            if f not in ["access"]:
                f = "objects/" + f
                writer(csvfile).writerow([f, officer])

parser = argparse.ArgumentParser(description='Copies TIFF and access files (JPGs or PDFs).')
parser.add_argument('source_directory', help='Path to the directory where the original digital objects (grouped in directories by officers) are.')
parser.add_argument('sip_directory', help='Path to the directory where each SIP should be placed.')
parser.add_argument('officers', help='Filepath to text file with officers (one per line).')
parser.add_argument('-a', '--aspace', help='Option to create the first column of an archivesspaceids.csv file.', action='store_true')
args = parser.parse_args()

officers = open(args.officers).readlines()
for o in officers:
    start_time = time()
    o = o.strip()
    print("Starting " + o + "...")
    sourceMaster = os.path.join(args.source_directory, r, "TIFFs")
    sourceAccess = os.path.join(args.source_directory, r, "PDFs")
    #  create Archivematica SIP directory and subdirectories
    makeSipDirectory(args.sip_directory, r)
    sipDirectory = os.path.join(args.sip_directory, "sip_" + r)
    metadataDirectory = os.path.join(sipDirectory, "metadata")
    objectsDirectory = os.path.join(sipDirectory, "objects")
    accessDirectory = os.path.join(objectsDirectory, "access")
    copyFiles(sourceMaster, objectsDirectory)
    copyFiles(sourceAccess, accessDirectory)
    removeThumbsDb(objectsDirectory)
    removeThumbsDb(accessDirectory)
    if args.aspace:
        createAspaceCsv(metadataDirectory, r, accessDirectory, objectsDirectory)
    elapsed_time = time() - start_time
    print(str(int(elapsed_time / 60)) + " minutes, " + str(int(elapsed_time % 60)) + " seconds elapsed")