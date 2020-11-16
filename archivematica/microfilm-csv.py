# Prep digitized microfilm files for ingest into Archivematica

import os
from csv import writer
from datetime import datetime


# Create new folders within each folder
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


def makePolicyRow(filename, microfilm):
    if microfilm in [
        'Rockefeller Sanitary Commission microfilm',
        'Bureau of Social Hygiene microfilm',
            'LSRM microfilm']:
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


def createRightsCsv(objectsDirectory, metadataDirectory, officer):
    filenames = os.listdir(objectsDirectory)
    with open(os.path.join(metadataDirectory, 'rights.csv'), 'w', newline='') as spreadsheet:
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
                    makeCopyrightRow(filename, findDate(f), "120"))
                writer(spreadsheet).writerow(makePolicyRow(filename, officer))
    print('Done!')
