#!/usr/bin/env python

# creates a CSV file containing PREMIS rights information to include in the /metadata directory of an Archivematica transfer
# script assumes that each file will have a Copyright Rights Basis and a Donor Rights Basis, and each Basis will have one associated Act

import glob, os, csv
from datetime import datetime
from os import path

# get dmID/find transfer directory - expects directory name to follow the convention FA/dmID/objects
dmID = input('Enter the digital media id: ')
objects_directory = path.join(dmID, 'objects')
metadata_directory = path.join(dmID, 'metadata')
filepath = path.join(dmID, 'metadata')
os.chdir(objects_directory)
filenames = sorted(glob.glob('**', recursive=True))

def get_info():
    global copyright_status
    global copyright_start_date
    global copyright_start_year
    global copyright_end_year
    global copyright_end_date
    global copyright_term
    global copyright_note
    global basis
    global other_start_date
    global copyright_act
    global copyright_act_restriction
    global copyright_act_note
    global other_basis_note
    global other_basis_act
    global other_basis_act_restriction
    global other_basis_act_note

    #get copyright info
    print("*** Enter copyright basis information ***")
    copyright_status = input('Copyrighted status? (copyrighted, publicdomain, unknown): ')
    copyright_start_year = input('Copyright start year YYYY: ')
    copyright_start_month = input('Copyright start month MM: ')
    copyright_start_day = input('Copyright start day DD: ')
    copyright_start_date = copyright_start_year + "-" + copyright_start_month + "-" + copyright_start_day
    copyright_term = input('Copyright term length (years): ')
    copyright_end_year = int(copyright_start_year) + int(copyright_term)
    copyright_end_date = str(copyright_end_year) + "-" + str(copyright_start_month) + "-" + str(copyright_start_day)
    print('Copyright end date is ' + copyright_end_date)
    copyright_note = input('Copyright note: ')
    copyright_act = input('Copyright act? (publish, disseminate): ')
    copyright_act_restriction = input('Copyright act restriction: (allow, disallow): ')
    copyright_act_note = input('Copyright act note: enter applicable content from signed agreement (to leave blank press ENTER): ')

    #get donor/policy info
    print("*** Enter policy/donor basis information ***")
    basis = input('Basis: (donor, policy): ')
    other_start_year = input(basis + ' start year YYYY: ')
    other_start_month = input(basis + 'start month MM: ')
    other_start_day = input(basis + 'start day DD: ')
    other_start_date = other_start_year + "-" + other_start_month + "-" + other_start_day
    other_basis_note = input(basis + ' note: include portions of donor agreement that pertain to access and use of the object (to leave blank press ENTER): ')
    other_basis_act = input(basis + ' act: (publish, disseminate): ')
    other_basis_act_restriction = input(basis + ' act restriction? (allow, disallow): ')
    other_basis_act_note = input(basis + ' note: explaination on act (to leave blank press ENTER): ')

def makeCopyrightRow(filename, copyright_status, copyright_start_year, copyright_start_date, copyright_end_date, copyright_term):
    global copyright_determination
    copyright_determination = datetime.now().strftime("%Y-%m-%d")
    #note = 'Copyright term ' + copyright_term + ' years from date of creation.'
    return makeRow(filename, "copyright", copyright_status, copyright_determination, 'us', copyright_start_date, copyright_end_date, copyright_note, copyright_act, copyright_act_restriction, copyright_determination, 'open',copyright_act_note)

def makeOtherRow(filename,basis):
    return makeRow(filename,basis,'','','',other_start_date,'open',other_basis_note,other_basis_act,other_basis_act_restriction,copyright_determination,'open',other_basis_act_note)

def makeRow(filename,basis,status,copyright_determination,jurisdiction,start_date,end_date,note,grant_act,grant_restriction,grant_start_date,grant_end_date,grant_note):
    row = []
    row.append(filename)
    row.append(basis)
    row.append(status)
    row.append(copyright_determination)
    row.append(jurisdiction)
    row.append(start_date)
    row.append(end_date)
    row.extend([''] * 2) #terms - for license basis #citation - for statute Basis
    row.append(note)
    row.append(grant_act)
    row.append(grant_restriction)
    row.append(grant_start_date)
    row.append(grant_end_date)
    row.append(grant_note)
    row.extend([''] * 3) #doc_id_type #doc_id_value #doc_id_role
    return row

def makeSpreadsheet(filepath, dmID, status, year, basis):
    with open(path.join(metadata_directory, 'rights.csv'), 'w') as spreadsheet:
        writer = csv.writer(spreadsheet)
        column_headings = ["file","basis","status","determination_date","jurisdiction","start_date","end_date","terms","citation", "note", "grant_act","grant_restriction","grant_start_date","grant_end_date","grant_note","doc_id_type","doc_id_value","doc_id_role"]
        writer.writerow(column_headings)
    #for each file, write copyright and donor rows
        for f in filenames:
            filename = 'objects/' + f
            writer.writerow(makeCopyrightRow(filename, copyright_status, copyright_start_year, copyright_start_date, copyright_end_date, copyright_term))
            writer.writerow(makeOtherRow(filename, basis))

get_info()

os.chdir('../..')

makeSpreadsheet(filepath, dmID, copyright_status, copyright_end_year, basis)

print("Done!")
print("The PREMIS spreadsheet is located in: ")
print("bcadmin/Desktop/" + metadata_directory + "/rights.csv")
