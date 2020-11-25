# Prep digitized microfilm files for ingest into Archivematica

import argparse
from csv import writer
from datetime import datetime
from os import listdir
from os.path import isdir, join

parser = argparse.ArgumentParser(
    description='Create archivesspaceids.csv and rights.csv files for a group of SIPs in a directory using a supplied TSV file.')
parser.add_argument(
    'location_of_sips',
    help='Path to the directory of SIPs requiring metadata files.')
parser.add_argument(
    'tsv_file',
    help='Full filepath of TSV file containing information to be included in metadata files. Expects 4 columns with order title, instance, date, refid.')
args = parser.parse_args()


def createAspaceCsv(metadata, access, refid):
    print("Creating archivesspaceids.csv...")
    aspacecsv = join(metadata, 'archivesspaceids.csv')
    with open(aspacecsv, 'w', newline='') as csvfile:
        f = "objects/" + access
        writer(csvfile).writerow([f, refid])


def getCopyrightEndDate(copyrightStartYear, copyrightTerm):
    copyrightEndYear = int(copyrightStartYear) + int(copyrightTerm)
    copyrightEndDate = str(copyrightEndYear) + "-12-31"
    return copyrightEndDate


def makeRow(
        filename,
        basis,
        status,
        determination_date,
        jurisdiction,
        start_date,
        end_date,
        note,
        grant_act,
        grant_restriction,
        grant_start_date,
        grant_end_date,
        grant_note):
    row = []
    row.append(filename)
    row.append(basis)
    row.append(status)
    row.append(determination_date)
    row.append(jurisdiction)
    row.append(start_date)
    row.append(end_date)
    # terms - for license basis citation - for statute basis
    row.extend([''] * 2)
    row.append(note)
    row.append(grant_act)
    row.append(grant_restriction)
    row.append(grant_start_date)
    row.append(grant_end_date)
    row.append(grant_note)
    row.extend([''] * 3)  # doc_id_type doc_id_value doc_id_role
    return row


def makeCopyrightRow(filename, copyrightStartYear, copyrightTerm):
    determination_date = datetime.now().strftime("%Y-%m-%d")
    start_date = copyrightStartYear + "-01-01"
    end_date = getCopyrightEndDate(copyrightStartYear, copyrightTerm)
    note = "Copyright term 120 years from date of creation."
    return makeRow(
        filename,
        'copyright',
        'copyrighted',
        determination_date,
        'us',
        start_date,
        end_date,
        note,
        'publish',
        'allow',
        '2019-01-01',
        'open',
        '')


def makePolicyRow(filename):
    note = "Rockefeller family/boards collections are open for research with select materials restricted."
    return makeRow(
        filename,
        'policy',
        '',
        '',
        '',
        '1974-01-01',
        'open',
        note,
        'disseminate',
        'allow',
        '2019-01-01',
        'open',
        '')


def createRightsCsv(objectsDirectory, metadataDirectory, end_date):
    filenames = listdir(objectsDirectory)
    with open(join(metadataDirectory, 'rights.csv'), 'w', newline='') as spreadsheet:
        column_headings = [
            "file",
            "basis",
            "status",
            "determination_date",
            "jurisdiction",
            "start_date",
            "end_date",
            "terms",
            "citation",
            "note",
            "grant_act",
            "grant_restriction",
            "grant_start_date",
            "grant_end_date",
            "grant_note",
            "doc_id_type",
            "doc_id_value",
            "doc_id_role"]
        writer(spreadsheet).writerow(column_headings)
        # for each file, write copyright and donor rows
        for f in filenames:
            if f not in ['access', 'service', '.DS_Store', 'Thumbs.db']:
                filename = "objects/" + f
                writer(spreadsheet).writerow(
                    makeCopyrightRow(filename, end_date, "120"))
                writer(spreadsheet).writerow(makePolicyRow(filename))


# get list of sip directories, save as a list
list_of_sips = [
    sip_directory for sip_directory in listdir(
        args.location_of_sips) if isdir(
            join(
                args.location_of_sips,
                sip_directory))]
# open tsv file, save as a list
rsc_list = open(args.tsv_file).readlines()
# strip, split list of metadata
for i, s in enumerate(rsc_list):
    rsc_list[i] = s.rstrip()
    rsc_list[i] = s.split("\t")
# iterate through sip directories, match metadata with directory
for sip in list_of_sips:
    sip_instance = ",".join(sip.split("_")[-2:]).lower()
    path_to_metadata = join(sip, "metadata")
    for f in listdir(join(sip, "objects")):
        if "pdf" in f:
            access_pdf = f
    for rsc_row in rsc_list:
        if rsc_row[1].lower().replace(" ", "") == sip_instance:
            # make archivesspaceids.csv file
            createAspaceCsv(path_to_metadata, access_pdf, rsc_row[-1])
            # make rights.csv file
            createRightsCsv(join(sip, "objects"), path_to_metadata, rsc_row[2])
            # remove match in rsc_list before iterating again
            rsc_list.remove(rsc_row)
        else:
            print("Match not found for {}".format(sip))
