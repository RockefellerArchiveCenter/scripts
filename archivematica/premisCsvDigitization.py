#!/usr/bin/env python

import os, csv, datetime

# get refid/find transfer directory
refid = raw_input('Enter the ArchivesSpace refid: ')
objects_directory = 'archivematica_sip_' + refid + '/objects/'
metadata_directory = 'archivematica_sip_' + refid + '/metadata/'
# filenames = os.listdir(objects_directory)
# print filenames

# get copyright info

# copyright status

def getCopyrightStatus():
    copyright_status_input = raw_input('Copyrighted? (y/n): ')
    if copyright_status_input.lower() == 'y' or copyright_status_input.lower() == 'yes':
        copyright_status = 'copyrighted'
    elif copyright_status_input.lower() == 'n' or copyright_status_input.lower() == 'no':
        copyright_status = 'publicdomain'
    else:
        copyright_status = '???'
    return copyright_status

copyright_status = getCopyrightStatus()

print copyright_status

#copyright determination date
def getCopyrightDeterminationDate():
    now = datetime.datetime.now()
    copyright_determination = now.strftime("%Y-%m-%d")
    return copyright_determination

determination_date = getCopyrightDeterminationDate()
print determination_date

# get donor info


# find and store all objects

#file	basis	status	determination_date	jurisdiction	start_date	end_date	terms	citation	note	grant_act	grant_restriction	grant_start_date	grant_end_date	grant_note	doc_id_type	doc_id_value	doc_id_role

def makeRow(filename,basis,status,determination_date,jurisdiction,start_date,end_date,terms,note,grant_act,grant_restriction,grant_start_date,grant_end_date,grant_note):
    row = []
    row.append(filename)
    row.append(basis)
    row.append(status)
    row.append(determination_date)
    row.append(jurisdiction)
    row.append(start_date)
    row.append(end_date)
    row.append('') #terms
    row.append('') #citation   
    row.append(note)    
    row.append(grant_act)    
    row.append(grant_restriction)    
    row.append(grant_start_date)    
    row.append(grant_end_date)  
    row.append(grant_note)
    row.append('') #doc_id_type
    row.append('') #doc_id_value
    row.append('')  #doc_id_role
    writer.writerow(row)

def makeCopyrightRow(filename):
    basis = 'copyright'
    determination_date = getCopyrightDeterminationDate()
    jurisdiction = 'us'
    start_date = '???'
    end_date =  '???'
    note = '???'
    grant_act = 'publish'
    grant_restriction = '???'
    grant_start_date = '???'
    grant_end_date = '???'
    grant_note = '???'
    makeRow(filename,basis,status,determination_date,jurisdiction,start_date,end_date,terms,note,grant_act,grant_restriction,grant_start_date,grant_end_date,grant_note)


def makeDonorRow(filename):
    basis = 'donor'
    status = ''
    determination_date = ''
    jurisdiction = ''
    start_date = '???'
    end_date = '???'
    note = '???'
    grant_act = 'disseminate'
    grant_restriction = '???'
    grant_start_date = '???'
    grant_end_date = '???'
    grant_note = '???'
    makeRow(filename,basis,status,determination_date,jurisdiction,start_date,end_date,terms,note,grant_act,grant_restriction,grant_start_date,grant_end_date,grant_note)

#for each object, write copyright and donor rows


print 'Creating a csv'
#os.chdir(metadata_directory)
spreadsheet = 'rights.csv'
writer = csv.writer(open(spreadsheet, 'w'))
column_headings = ["file","basis","status","determination_date","jurisdiction","start_date","end_date","terms","citation","note","grant_act","grant_restriction","grant_start_date","grant_end_date","grant_note","doc_id_type","doc_id_value","doc_id_role"]
print column_headings
writer.writerow(column_headings)
#for filename in filenames:
#    makeRow(filename,refid)
#print 'Done!'