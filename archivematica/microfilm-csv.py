# Prep digitized microfilm files for ingest into Archivematica

import argparse
import os
from csv import writer
from datetime import datetime
from shutil import copy2

parser = argparse.ArgumentParser(description='Copies TIFF and PDF files.')
parser.add_argument(
    'sip_directory',
    help='Path to the directory where each SIP should be placed.')
parser.add_argument(
    'source_directory',
    help='Path to the directory where the original digital objects (grouped in directories by reel) are.')
parser.add_argument(
    'collection',
    help='Directory name that corresponds to the microfilm collection.')
parser.add_argument(
    'reel', help='Directory name that corresponds to the reel.')
parser.add_argument(
    '-a',
    '--aspace',
    help='Option to create the first column of an archivesspaceids.csv file.',
    action='store_true')
parser.add_argument(
    '-p',
    '--premis',
    help='Option to a rights.csv file. Assumes creation year is in filename.',
    action='store_true')
args = parser.parse_args()

# Create new folder and define name of new folder (probably use txt file
# that list folders like RFOD script)#
path_to_reel = os.path.join(args.source_directory, args.collection, args.reel)
list_of_folders = [folder for folder in os.listdir(
    path_to_reel) if os.path.isdir(os.path.join(path_to_reel, folder))]


def package_transfer(sip_directory, reel_path, collection, reel, folder):
    print("Starting {} {} {}...".format(collection, reel, folder))
    make_sip_directory(sip_directory, collection, reel, folder)
    sip_directory = os.path.join(args.sip_directory, "{}_{}_{}".format(collection.replace(" ", "_"), reel.replace(" ", "_"), folder.replace(" ", "_")))
    copy_files(
        os.path.join(
            reel_path, folder, "Master"), os.path.join(
            sip_directory, "objects"))
    copy_files(
        os.path.join(
            reel_path,
            folder,
            "Service Edited"),
        os.path.join(
            sip_directory,
            "objects",
            "access"))

# Create new folders within each folder


def copy_files(source, destination):
    print("Copying files from " + source + " to " + destination + "...")
    for f in os.listdir(source):
        if not f[-5:] == "bs.db":
            copy2(os.path.join(source, f), destination)


def make_sip_directory(topDirectory, collection, reel, folder):
    print("Making SIP directory...")
    microfilmfolder = os.path.join(topDirectory, "{}_{}_{}".format(collection.replace(" ", "_"), reel.replace(" ", "_"), folder.replace(" ", "_")))
    os.mkdir(os.path.join(topDirectory, microfilmfolder))
    targetDirectory = os.path.join(topDirectory, microfilmfolder)
    for subdirectory in ["logs", "metadata", "objects"]:
        os.mkdir(os.path.join(targetDirectory, subdirectory))
    objectsDirectory = os.path.join(targetDirectory, "objects")
    os.mkdir(os.path.join(objectsDirectory, "access"))


# Copy access files in folder


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


for folder in list_of_folders:
    package_transfer(args.sip_directory, path_to_reel, args.collection, args.reel, folder)
