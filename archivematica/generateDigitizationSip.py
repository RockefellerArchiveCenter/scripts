#!/usr/bin/env python

import os, argparse, re
from csv import writer
from shutil import copy2
from PyPDF2 import PdfFileWriter, PdfFileReader

def makeSipDirectory(topDirectory, refid):
    print("Making SIP directory...")
    refid = "sip_" + refid
    os.mkdir(os.path.join(topDirectory, refid))
    targetDirectory = os.path.join(topDirectory, refid)
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
        copy2(os.path.join(source, f), destination)
        if f[-7:-4] in ["_me", "_se"]:
            newName = f[:-7] + f[-4:]
            os.replace(os.path.join(destination, f), os.path.join(destination, newName))

def removeThumbsDb(directory):
    for f in os.listdir(directory):
        if f[-5:] == "bs.db":
            os.remove(os.path.join(directory, f))

def remove1stPagePdf(pdf):
    infile = PdfFileReader(pdf, 'rb')
    output = PdfFileWriter()
    for i in range(infile.getNumPages()):
        if i not in [0]:
            p = infile.getPage(i)
            output.addPage(p)
    with open('newfile.pdf', 'wb') as f:
        output.write(f)
    os.replace("newfile.pdf", pdf)

def removeCitationSheet(objects, access):
    print("Removing citation sheets...")
    for f in os.listdir(objects):
        if f[-8:-4] == "_001":
            os.remove(os.path.join(objects, f))
    if checkAccessPdf(access):
        for f in os.listdir(access):
            remove1stPagePdf(os.path.join(access, f))
    else:
        for f in os.listdir(access):
            if f[-8:-4] == "_001":
                os.remove(os.path.join(access, f))
                
def createAspaceCsv(metadata, refid, access, objects):
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
                writer(csvfile).writerow([f, refid])
        

parser = argparse.ArgumentParser(description='Copies TIFF and access files (JPGs or PDFs).')
parser.add_argument('source_directory', help='Path to the directory where the original digital objects (grouped in directories by refids) are.')
parser.add_argument('sip_directory', help='Path to the directory where each SIP should be placed.')
parser.add_argument('refids', help='Filepath to text file with refids (one per line).')
parser.add_argument('-c', '--citation', help='Option to remove first "page" from each set of files, including concatenated PDFs.', action='store_true')
parser.add_argument('-a', '--aspace', help='Option to create an archivesspaceids.csv file. Assumes that refid is part of filename.', action='store_true')
args = parser.parse_args()

refids = open(args.refids).readlines()
for r in refids:
    r = r.replace('\n', '')
    print("Starting " + r + "...")
    sourceMaster = os.path.join(args.source_directory, r, "master")
    sourceAccess = os.path.join(args.source_directory, r, "service_edited")
    #  create Archivematica SIP directory and subdirectories
    makeSipDirectory(args.sip_directory, r)
    sipDirectory = os.path.join(args.sip_directory, "sip_" + r)
    metadataDirectory = os.path.join(sipDirectory, "metadata")
    objectsDirectory = os.path.join(sipDirectory, "objects")
    accessDirectory = os.path.join(objectsDirectory, "access")
    copyFiles(sourceMaster, objectsDirectory)
    copyFiles(sourceAccess, accessDirectory)
    if args.citation:
        removeCitationSheet(objectsDirectory, accessDirectory)
    if checkAccessPdf(accessDirectory):
        copyFiles(accessDirectory, objectsDirectory)
    removeThumbsDb(objectsDirectory)
    removeThumbsDb(accessDirectory)
    createAspaceCsv(metadataDirectory, r, accessDirectory, objectsDirectory)