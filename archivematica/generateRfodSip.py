#!/usr/bin/env python

import os, argparse, re
from csv import writer
from shutil import copy2
from time import time
from datetime import datetime

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
        
def findDate(date):
    if date[-4:].isdigit() and int(date[-4:]) >= 1900 and int(date[-4:]) <= 2000:
        year=date[-4:]
        return year
    else:
        x=-5
        y=-1
        for r in range(len(date)):
            if date[x:y].isdigit() and int(date[x:y]) >= 1900 and int(date[x:y]) <= 2000:
                year=date[x:y]
                return year
                break
            else:
                x += -1
                y += -1
        
def getCopyrightEndDate(copyrightStartYear, copyrightTerm):
    copyrightEndYear = int(copyrightStartYear) + int(copyrightTerm)
    copyrightEndDate = str(copyrightEndYear) + "-12-31"
    return copyrightEndDate
    
def makeRow(filename,basis,status,determination_date,jurisdiction,start_date,end_date,note,grant_act,grant_restriction,grant_start_date,grant_end_date,grant_note):
    row = []
    row.append(filename)
    row.append(basis)
    row.append(status)
    row.append(determination_date)
    row.append(jurisdiction)
    row.append(start_date)
    row.append(end_date)
    row.extend([''] * 2) #terms - for license basis #citation - for statute basis
    row.append(note)
    row.append(grant_act)
    row.append(grant_restriction)
    row.append(grant_start_date)
    row.append(grant_end_date)
    row.append(grant_note)
    row.extend([''] * 3) #doc_id_type #doc_id_value #doc_id_role
    return row
    
def makeCopyrightRow(filename, copyrightStartYear, copyrightTerm):
    determination_date = datetime.now().strftime("%Y-%m-%d")
    start_date = copyrightStartYear + "-01-01"
    end_date =  getCopyrightEndDate(copyrightStartYear, copyrightTerm)
    note = 'Work for hire - copyright term ' + copyrightTerm + ' years from date of creation. Copyright held by the Rockefeller Foundation.'
    return makeRow(filename,'copyright','copyrighted',determination_date,'us',start_date,end_date,note,'publish','allow','2019-01-01','open','')
    
def makePolicyRow(filename, officer):
    if officer in ['Arnett','Davis', 'Pearce', 'Rose', 'Shepardson', 'Trowbridge']:
        note = 'General Education Board records are open to research.'
    else:
        note = "Rockefeller Foundation records are open after 20 years from creation. Officers' diaries are open after the diarist is deceased."
    return makeRow(filename,'policy','','','','1974-01-01','open',note,'disseminate','allow','2019-01-01','open','')
    
def createRightsCsv(objectsDirectory, metadataDirectory, officer):
    filenames = os.listdir(objectsDirectory)
    with open(os.path.join(metadataDirectory, 'rights.csv'), 'w') as spreadsheet:
        column_headings = ["file","basis","status","determination_date","jurisdiction","start_date","end_date","terms","citation","note","grant_act","grant_restriction","grant_start_date","grant_end_date","grant_note","doc_id_type","doc_id_value","doc_id_role"]
        writer(spreadsheet).writerow(column_headings)
        #for each file, write copyright and donor rows
        for f in filenames:
            if f not in ['access', 'service', '.DS_Store', 'Thumbs.db']:
                filename = "objects/" + f
                writer(spreadsheet).writerow(makeCopyrightRow(filename, findDate(f), "120"))
                writer(spreadsheet).writerow(makePolicyRow(filename, officer))
    print('Done!')

parser = argparse.ArgumentParser(description='Copies TIFF and PDF files.')
parser.add_argument('source_directory', help='Path to the directory where the original digital objects (grouped in directories by officers) are.')
parser.add_argument('sip_directory', help='Path to the directory where each SIP should be placed.')
parser.add_argument('officers', help='Filepath to text file with officers (one per line).')
parser.add_argument('-a', '--aspace', help='Option to create the first column of an archivesspaceids.csv file.', action='store_true')
parser.add_argument('-p', '--premis', help='Option to a rights.csv file. Assumes creation year is in filename.', action='store_true')
args = parser.parse_args()

officers = open(args.officers).readlines()
for o in officers:
    o = o.strip()
    officerDirectory = os.path.join(args.source_directory, o)
    diaries = os.listdir(os.path.join(officerDirectory, "TIFFs", "Master"))
    print(o + ': ' + ', '.join(diaries))
    for d in diaries:
        if d not in ['.DS_Store', 'Thumbs.db']: 
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
            if args.premis:
                createRightsCsv(objectsDirectory, metadataDirectory, o)
            elapsed_time = time() - start_time
            print(str(int(elapsed_time / 60)) + " minutes, " + str(int(elapsed_time % 60)) + " seconds elapsed")