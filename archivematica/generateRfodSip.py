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

def copyFiles(source, destination):
    print("Copying files from " + source + " to " + destination + "...")
    for f in os.listdir(source):
        if not f[-5:] == "bs.db":
            copy2(os.path.join(source, f), destination)

                
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
                writer(csvfile).writerow([f])

parser = argparse.ArgumentParser(description='Copies TIFF and PDF files.')
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
    sourceMaster = os.path.join(args.source_directory, o, "TIFFs")
    sourceAccess = os.path.join(args.source_directory, o, "PDFs")
    #  create Archivematica SIP directory and subdirectories
    makeSipDirectory(args.sip_directory, o)
    sipDirectory = os.path.join(args.sip_directory, "sip_" + o)
    metadataDirectory = os.path.join(sipDirectory, "metadata")
    objectsDirectory = os.path.join(sipDirectory, "objects")
    accessDirectory = os.path.join(objectsDirectory, "access")
    copyFiles(sourceMaster, objectsDirectory)
    copyFiles(sourceAccess, accessDirectory)
    if args.aspace:
        createAspaceCsv(metadataDirectory, ro, accessDirectory, objectsDirectory)
    elapsed_time = time() - start_time
    print(str(int(elapsed_time / 60)) + " minutes, " + str(int(elapsed_time % 60)) + " seconds elapsed")