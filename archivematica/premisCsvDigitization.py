#!/usr/bin/env python

# creates a CSV file containing PREMIS rights information to include in the /metadata directory of an Archivematica transfer
# script assumes that each file will have a Copyright Rights Basis and a Donor Rights Basis, and each Basis will have one associated Act

import csv, argparse
from datetime import datetime
from os import path, listdir

# copyright applicable end date
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

def makeCopyrightRow(filename, status, copyrightStartYear, copyrightTerm):
    determination_date = datetime.now().strftime("%Y-%m-%d")
    start_date = copyrightStartYear + "-01-01"
    end_date =  getCopyrightEndDate(copyrightStartYear, copyrightTerm)
    note = 'Copyright term' + copyrightTerm + ' years from date of creation.'
    return makeRow(filename,'copyright',status,determination_date,'us',start_date,end_date,note,'publish','allow','2019-01-01','open','')


def makeOtherRow(filename, basis):
    start_date = '1975-01-01'
    note = 'Open for research.'
    return makeRow(filename,basis,'','','',start_date,'open',note,'disseminate','allow','2019-01-01','open','')

def makeSpreadsheet(filepath, refid, status, year, basis):
    sipDirectory = path.join(filepath, "sip_" + refid)
    metadataDirectory = path.join(sipDirectory, "metadata")
    objectsDirectory = path.join(sipDirectory, "objects")
    filenames = listdir(objectsDirectory)
    spreadsheet = path.join(metadataDirectory, 'rights.csv')
    writer = csv.writer(open(spreadsheet, 'w'))
    column_headings = ["file","basis","status","determination_date","jurisdiction","start_date","end_date","terms","citation","note","grant_act","grant_restriction","grant_start_date","grant_end_date","grant_note","doc_id_type","doc_id_value","doc_id_role"]
    writer.writerow(column_headings)
    #for each file, write copyright and donor rows
    for f in filenames:
        if f not in ['access', 'service', '.DS_Store']:
            filename = "objects/" + f
            writer.writerow(makeCopyrightRow(filename, status, year, "120"))
            writer.writerow(makeOtherRow(filename, basis))
    print('Done!')

parser = argparse.ArgumentParser(description="Creates a csv file for Archivematica's PREMIS rights csv feature")
parser.add_argument('sip_directory', help='Path to the directory where each SIP is a subdirectory')
parser.add_argument('refids', help='Filepath to text file with refids and dates, separated by a tab and one per line.')
parser.add_argument('status', choices=['copyrighted', 'publicdomain', 'unknown'])
parser.add_argument('basis', choices=['donor', 'policy'])
args = parser.parse_args()

refids = {}
listOfRefids = open(args.refids).readlines()
for l in listOfRefids:
    key, value = l.strip().split('\t')
    refids.update({key : value})
    
for r, y in refids.items():
    makeSpreadsheet(args.sip_directory, r, args.basis, y, args.basis)


