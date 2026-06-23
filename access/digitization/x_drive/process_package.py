#!/usr/bin/env python3

# Pre-run requirements
# Get on RAC network
# Connect to X drive
# Update AWS session credentials

import argparse
from datetime import datetime
from os import getenv
from pathlib import Path
from shutil import rmtree, copytree

import bagit
import boto3
from requests import Session

AQUILA_BASEURL = getenv('AQUILA_BASEURL')
AWS_ROLE_NAME = getenv('AWS_ROLE_NAME')
AWS_BUCKET_NAME = getenv('AWS_BUCKET_NAME')
RESTRICTED_DIR = getenv('RESTRICTED_DIR')
UPLOADED_DIR = getenv('UPLOADED_DIR')
INVALID_DIR = getenv('INVALID_DIR')

class AquilaClient(object):
    """Client for Aquila"""

    def __init__(self, baseurl):
        self.session = Session()
        self.baseurl = baseurl

    def get_rights_data(self, rights_ids, start_date, end_date):
        """Returns rights data from Aquila.
        
        Args:
            rights_ids (str): comma-separated list of rights identifiers
            start_date (str): ISO-formatted start date
            end_date (str): ISO-formatted end date

        Returns:
            (list): rights statements
        """
        data = {
            'identifiers': rights_ids,
            'start_date': start_date,
            'end_date': end_date
        }
        resp = self.session.post(
            f'{self.baseurl.rstrip("/")}/rights-assemble/',
            json=data)
        resp.raise_for_status()
        return resp.json()['rights_statements']


def main(
    base_dir, 
    transaction_number, 
    refid, 
    rights_ids, 
    start_date,
    end_date):
    """Main method which calls all other submethods."""
    
    aws_session = boto3.Session(role_name=AWS_ROLE_NAME)
    s3_client = aws_session.client('s3')
    aquila_client = AquilaClient(AQUILA_BASEURL)

    package_path = Path(base_dir, transaction_number)
    assert package_path.is_dir(), f"Expected package with transaction {transaction_number} does not exist at {package_path}"

    remove_unwanted_files(package_path)
    renamed_path = rename_files(package_path, refid)
            
    if is_restricted(
            rights_ids, 
            start_date, 
            end_date, 
            aquila_client):
        move_to_dir(renamed_path, RESTRICTED_DIR)
    else:
        if is_valid_package(renamed_path):
            create_bag(renamed_path)
            tarball_path = create_tarball(renamed_path)
            upload_package(tarball_path, s3_client)
            tarball_path.rename(Path(UPLOADED_DIR, tarball_path.name))
        else:
            move_to_dir(renamed_path, INVALID_DIR)

def get_active_rights_acts(acts):
    """Filters out active rights acts."""

    current_date = datetime.now()
    for idx, act in reversed(list(enumerate(acts))):
        if act.get('end_date'):
            statement_end = datetime.strptime(act['end_date'], "%Y-%m-%d")
            if (current_date > statement_end):
                acts.pop(idx)
    return acts

def is_restricted(rights_ids, start_date, end_date, aquila_client):
    """Determines if object is restricted.
    
    Args:
        rights_ids (str): comma-separated list of rights IDs
        start_date (str): ISO-formatted start date of digitized object
        end_date (str): ISO-formatted end date of digitized object
        aquila_client (AquilaClient): instance of client for Aquila

    Returns:
        (bool): indication of whether package is restricted or not
    """

    rights_statements = aquila_client.get_rights_data(rights_ids, start_date, end_date)
    for rights_statement in rights_statements:
        for granted in get_active_rights_acts(rights_statement['rights_granted']):
            if granted['act'] in ['publish', 'disseminate'] and granted['grant_restriction'] != 'allow':
                return True
    return False

def move_to_dir(current_path, target_dir):
    """Move digitized directory to new target as directory.
    
    Args:
        current_path (pathlib.Path): current path of digitized object
        target_dir (pathlib.path): path for new digitized object
    """

    copytree(current_path, target_dir)
    rmtree(current_path)

def is_valid_package(dir_path):
    """Validates package structure and assets.
    
    Args:
        dir_path (pathlib.Path): path of digitized object to validate.
    """

    for expected_subdir in ['master', 'master_edited', 'service_edited']:
        assert (dir_path / expected_subdir).is_dir()
    assert len([(dir_path / 'master').iterdir()]) == len([(dir_path / 'master_edited').iterdir()])
    assert (dir_path / 'service_edited' / "*.pdf").is_file()

def remove_unwanted_files(dir_path):
    """Removes unwanted files from directory.
    
    Args:
        dir_path (pathlib.Path): directory from which files should be removed.
    """

    for fp in dir_path.rglob("*"):
        if fp.name in ["Thumbs.db", ".DS_Store"]:
            fp.unlink()

def rename_files(dir_path, refid):
    """Renames files associated with a digital object to match RAC specifications.
    
    Args:
        dir_path (pathlib.Path): path of digital object to rename
        refid (str): ref ID for digital object, used as basis for file renaming
    """

    for fp in dir_path.iter_dir():
        if fp.is_file():
            iterator = str(int(fp.stem.split("_")[-1])).zfill(4) if len(fp.stem.split("_") > 1) else None
            if iterator:
                new_name = fp.with_name(f"{refid}_{iterator}{fp.suffix}")
            else:
                new_name = fp.with_name(f"{refid}{fp.suffix}")
            fp.rename(new_name)
    copytree(dir_path, dir_path.with_name(refid))
    rmtree(dir_path)

def create_bag(dir_path):
    """Creates BagIt bag from digital object.
    
    Args:
        dir_path (pathlib.Path): path of digital object to bag
    """

    bag = bagit.Bag(str(dir_path))
    bag.save()

def create_tarball(dir_path):
    """Create tarball from bagged path.
    
    Args:
        dir_path (pathlib.Path): path of digital object to tarball

    Returns:
        tar_path (pathlib.Path): path to tarball
    """

    tar_path = dir_path.with_name(f"{str(dir_path)}.tar.gz")
    with open(tar_path, "w:gz") as tf:
        for fp in dir_path.iter_dir():
            tf.add(fp.relative_to(dir_path))
    return tar_path

def upload_package(package_path, client):
    """Uploads package to S3 bucket.
    
    Args:
        package_path (pathlib.Path): Path of file to upload.
        client (boto3.client): S3 client
    """
    client.upload_file(str(package_path), AWS_BUCKET_NAME, package_path.name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Assesses rights status, restructures files, and uploads to S3')
    parser.add_argument('base_dir', help='The base directory to iterate through.')
    parser.add_argument('transaction_number', help='Aeon transaction number for package')
    parser.add_argument('refid', help='ArchivesSpace Ref ID for package')
    parser.add_argument('rights_ids', help='Aquila rights IDs for package')
    parser.add_argument('start_date', help='Start date for package', type=datetime.fromisoformat)
    parser.add_argument('end_date', help='End date for package', type=datetime.fromisoformat)
    args = parser.parse_args()
    main(
        args.base_dir, 
        args.transaction_number, 
        args.refid, 
        args.rights_ids, 
        args.start_date,
        args.end_date)