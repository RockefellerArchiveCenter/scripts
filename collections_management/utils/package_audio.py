#!/usr/bin/env python

# usage: package_audio.py [-h] [--av_number AV_NUMBER] directory

# Packages audiovisual assets in preparation for ingest.

# positional arguments:
#   directory             Directory in which files to be packaged are located.

# options:
#   -h, --help            show this help message and exit
#   --av_number AV_NUMBER, -a AV_NUMBER
#                         AV Number of object to be packaged.

# This script assumes the following:
#   1. Directories are named according to a numeric AV number (i.e. "15754" rather than "AV 15754")
#   2. Files within directory start with that same numeric AV number, for example "15754.mp3"
#   3. Files within directory may have a suffix to indicate multiple parts, for example "15754_01.wav"

from argparse import ArgumentParser
import logging
from pathlib import Path
import re
import tarfile

from asnake.aspace import ASpace
import bagit
from shutil import rmtree

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(message)s')
logging.getLogger("bagit").setLevel(logging.ERROR)

DEST_DIR = "~/Desktop"

def main(initial_dir, av_number):
    if av_number:
        handle_package(av_number, initial_dir)
    else:
        for fp in Path(initial_dir).iterdir():
            if fp.is_dir():
                handle_package(fp.stem, initial_dir)

def handle_package(raw_av_number, initial_dir):
    """Main method which handles logic for each directory."""
    av_number_display, av_number_numeric = parse_av_number(raw_av_number)
    logging.info(f"Processing {av_number_display}")

    source_dir = Path(initial_dir, av_number_numeric)
    if not source_dir.is_dir():
        raise FileNotFoundError(f"Could not find expected directory {str(source_dir)}.")
    
    refid = get_refid_from_av_number(av_number_display)
    logging.debug(f"Found ref_id {refid} for {av_number_display}")
    
    directory_to_bag = create_bag_structure(source_dir, refid, av_number_numeric)
    logging.debug(f"Structure for {av_number_display} / {refid} created")
    
    bag_path = create_bag(directory_to_bag)
    logging.debug(f"Bag for {av_number_display} / {refid} created")

    bag_path.rename(Path(DEST_DIR, bag_path.name))

def parse_av_number(av_number):
    """Returns normalized versions of the AV number.

    Args:
        av_number (str): a raw AV number.
    
    Returns:
        numbers (str, str): display and numeric values for the AV number.
    """
    av_number_numeric = av_number.lstrip("AV ").lstrip("av ")
    return f"AV {av_number_numeric}", av_number_numeric

def get_refid_from_av_number(av_number):
    """Returns a refid for an AV number.

    Relies on an ArchivesSnake config file (~/.archivessnake.yml) for credentials.

    Args:
        av_number: A display AV number (prefixed with "AV")
    
    Returns:
        refid (str): AS refid
    """
    as_client = ASpace().client
    results = as_client.get(f"repositories/{as_client.config['repo_id']}/search?q='{av_number.replace(' ', '+')}'&type[]=archival_object&page=1&fields[]=ref_id").json()
    if results['total_hits'] != 1:
        raise Exception(f"Expected exactly one result for {av_number}, got {results['total_hits']}")
    return results['results'][0]['ref_id']

def create_bag_structure(source_dir, refid, av_number):
    """Creates a directory using the refid and moves/renames files matching AV number.

    Removes the original source directory once files have been moved.

    Args:
        source_dir (pathlib.Path): filepath of directory containing files to be bagged.
        refid (str): refid for the directory of files.
        av_number (str): numeric AV number for the directory of files.
    
    Returns:
        bag_path (pathlib.Path): filepath of bag structure
    """
    new_dir = Path(source_dir.parent, refid)
    matching_files = source_dir.glob(f'*{av_number}*')
    new_dir.mkdir()
    for fp in matching_files:
        new_filename = re.sub(av_number, refid, fp.name)
        fp.rename(Path(new_dir, new_filename))
    rmtree(source_dir)
    return new_dir

def create_bag(source_dir):
    """Creates a serialized bag from a directory.

    Original directory is removed once tarfile has been created.
    
    Args:
        source_dir (pathlib.Path): directory to be bagged.

    Returns:
        bag_path (pathlib.Path): path to created bag
    """
    bagit.make_bag(source_dir)
    destination = Path(source_dir.parent, f"{source_dir.stem}.tar.gz")
    with tarfile.open(destination, "w:gz", compresslevel=1) as tar:
        tar.add(source_dir, arcname=source_dir.name)
    rmtree(source_dir)
    return destination

if __name__ == '__main__':
    parser = ArgumentParser(description='Packages audiovisual assets in preparation for ingest.')
    parser.add_argument(
        'directory',
        help='Directory in which files to be packaged are located.')
    parser.add_argument(
        '--av_number', '-a',
        help='AV Number of object to be packaged.')
    args = parser.parse_args()
    main(args.directory, args.av_number)