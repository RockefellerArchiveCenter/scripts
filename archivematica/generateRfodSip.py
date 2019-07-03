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
    os.mkdir(os.path.join(objectsDirectory, "service"))
    os.mkdir(os.path.join(objectsDirectory, "access"))

def copyFiles(source, destination):
    print("Copying files from " + source + " to " + destination + "...")
    for f in os.listdir(source):
        if not f[-5:] == "bs.db":
            copy2(os.path.join(source, f), destination)
            if f[-7:-4] in ["_me", "_se"]:
                newName = f[:-7] + f[-4:]
                os.replace(os.path.join(destination, f), os.path.join(destination, newName))
                
def createAspaceCsv(metadata, access):
    print("Creating archivesspaceids.csv...")
    aspacecsv = os.path.join(metadata, 'archivesspaceids.csv')
    with open(aspacecsv, 'w') as csvfile:
        f = "objects/" + access
        writer(csvfile).writerow([f])

parser = argparse.ArgumentParser(description='Copies TIFF and PDF files.')
parser.add_argument('source_directory', help='Path to the directory where the original digital objects (grouped in directories by officers) are.')
parser.add_argument('sip_directory', help='Path to the directory where each SIP should be placed.')
parser.add_argument('officers', help='Filepath to text file with officers (one per line).')
parser.add_argument('-a', '--aspace', help='Option to create the first column of an archivesspaceids.csv file.', action='store_true')
args = parser.parse_args()

officers = open(args.officers).readlines()
for o in officers:
    o = o.strip()
    officerDirectory = os.path.join(args.source_directory, o)
    diaries = os.listdir(os.path.join(officerDirectory, "TIFFs", "Master"))
    for d in diaries:
        start_time = time()
        print("Starting " + d + "...")
        sourceMaster = os.path.join(officerDirectory, "TIFFs", "Master", d)
        sourceService = os.path.join(officerDirectory, "TIFFs", "Master-Edited", d)
        accessPdf = os.path.join(officerDirectory, "PDFs", d + ".pdf")
        #  create Archivematica SIP directory and subdirectories
        makeSipDirectory(args.sip_directory, d)
        sipDirectory = os.path.join(args.sip_directory, "sip_" + d)
        metadataDirectory = os.path.join(sipDirectory, "metadata")
        objectsDirectory = os.path.join(sipDirectory, "objects")
        serviceDirectory = os.path.join(objectsDirectory, "service")
        accessDirectory = os.path.join(objectsDirectory, "access")
        copyFiles(sourceMaster, objectsDirectory)
        copyFiles(sourceService, serviceDirectory)
        copy2(accessPdf, accessDirectory)
        copy2(accessPdf, objectsDirectory)
        if args.aspace:
            createAspaceCsv(metadataDirectory, d + ".pdf")
        elapsed_time = time() - start_time
        print(str(int(elapsed_time / 60)) + " minutes, " + str(int(elapsed_time % 60)) + " seconds elapsed")