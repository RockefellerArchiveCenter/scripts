# Prep digitized microfilm files for ingest into Archivematica

import argparse
import os
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
args = parser.parse_args()

# Create new folder and define name of new folder (probably use txt file
# that list folders like RFOD script)#
path_to_reel = os.path.join(args.source_directory, args.collection, args.reel)
list_of_folders = [folder for folder in os.listdir(
    path_to_reel) if os.path.isdir(os.path.join(path_to_reel, folder))]


def package_transfer(sip_directory, reel_path, collection, reel, folder):
    print("Starting {} {} {}...".format(collection, reel, folder))
    make_sip_directory(sip_directory, collection, reel, folder)
    sip_directory = os.path.join(
        args.sip_directory, "{}_{}_{}".format(
            collection.replace(
                " ", "_"), reel.replace(
                " ", "_"), folder.replace(
                    " ", "_")))
    original_directory = os.path.join(reel_path, folder)
    objects_directory = os.path.join(sip_directory, "objects")
    copy_files(os.path.join(original_directory, "Master"), objects_directory)
    copy_files(
        os.path.join(
            original_directory,
            "Service Edited"),
        os.path.join(
            objects_directory,
            "access"))
    copy_files(
        os.path.join(
            original_directory,
            "Service Edited"),
        objects_directory)

# Create new folders within each folder


def copy_files(source, destination):
    print("Copying files from " + source + " to " + destination + "...")
    for f in os.listdir(source):
        if not f[-5:] == "bs.db":
            copy2(os.path.join(source, f), destination)


def make_sip_directory(topDirectory, collection, reel, folder):
    print("Making SIP directory...")
    microfilmfolder = os.path.join(
        topDirectory, "{}_{}_{}".format(
            collection.replace(
                " ", "_"), reel.replace(
                " ", "_"), folder.replace(
                    " ", "_")))
    os.mkdir(os.path.join(topDirectory, microfilmfolder))
    targetDirectory = os.path.join(topDirectory, microfilmfolder)
    for subdirectory in ["logs", "metadata", "objects"]:
        os.mkdir(os.path.join(targetDirectory, subdirectory))
    objectsDirectory = os.path.join(targetDirectory, "objects")
    os.mkdir(os.path.join(objectsDirectory, "access"))


for folder in list_of_folders:
    package_transfer(
        args.sip_directory,
        path_to_reel,
        args.collection,
        args.reel,
        folder)
