#!/usr/bin/env python3

import argparse
import tarfile
from datetime import datetime
from pathlib import Path
from os import getenv
from shutil import rmtree, copytree

import bagit
import boto3
import pandas

AWS_ROLE_NAME = getenv('AWS_ROLE_NAME')
AWS_BUCKET_NAME = getenv('AWS_BUCKET_NAME')

RESTRICTED_DIR = getenv("RESTRICTED_DIR")
UPLOADED_DIR = getenv("UPLOADED_DIR")
INVALID_DIR = getenv("INVALID_DIR")


def main(spreadsheet_path, restricted):
    """Main method which calls all other submethods."""
    
    aws_session = boto3.Session(profile_name=AWS_ROLE_NAME)
    s3_client = aws_session.client('s3')

    df = pandas.read_excel(spreadsheet_path, header=0)
    for index, row in df.iterrows():
        refid = row['refid'].strip()
        package_path = Path(row['current_path'].strip())
        assert package_path.is_dir(), f"Package does not exist at {package_path}"

        remove_unwanted_files(package_path)

        renamed_path = rename_files(package_path, refid)
        if restricted:
            move_to_dir(renamed_path, RESTRICTED_DIR)
        else:
            bagit.make_bag(str(renamed_path))
            tarball_path = create_tarball(renamed_path)
            upload_package(tarball_path, s3_client)
            Path(UPLOADED_DIR).mkdir(exist_ok=True)
            tarball_path.rename(Path(UPLOADED_DIR, tarball_path.name))

def get_active_rights_acts(acts):
    """Filters out active rights acts."""

    current_date = datetime.now()
    for idx, act in reversed(list(enumerate(acts))):
        if act.get('end_date'):
            statement_end = datetime.strptime(act['end_date'], "%Y-%m-%d")
            if (current_date > statement_end):
                acts.pop(idx)
    return acts

def move_to_dir(current_path, target_dir):
    """Move digitized directory to new target as directory.
    
    Args:
        current_path (pathlib.Path): current path of digitized object
        target_dir (str): path for new digitized object
    """
    dest_path = Path(target_dir, current_path.stem)
    Path(target_dir).mkdir(exist_ok=True, parents=True)
    copytree(current_path, dest_path)
    rmtree(current_path)

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
    for fp in dir_path.rglob("*"):
        if fp.is_file():
            iterator = str(int(fp.stem.split("_")[-1])).zfill(4) if len(fp.stem.split("_")) > 1 else None
            if iterator:
                new_name = fp.with_name(f"{refid}_{iterator}{fp.suffix}")
            else:
                new_name = fp.with_name(f"{refid}{fp.suffix}")
            fp.rename(new_name)
    copytree(dir_path, dir_path.with_name(refid))
    rmtree(dir_path)
    return(dir_path.with_name(refid))

def create_tarball(dir_path):
    """Create tarball from bagged path.
    
    Args:
        dir_path (pathlib.Path): path of digital object to tarball

    Returns:
        tar_path (pathlib.Path): path to tarball
    """
    tar_path = dir_path.with_name(f"{dir_path.name}.tar.gz")
    with tarfile.open(tar_path, "w:gz") as tf:
        tf.add(dir_path, arcname=dir_path.name)
    return tar_path

def upload_package(package_path, client):
    """Uploads package to S3 bucket.
    
    Args:
        package_path (pathlib.Path): Path of file to upload.
        client (boto3.client): S3 client
    """
    client.upload_file(str(package_path), AWS_BUCKET_NAME, package_path.name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Validates, restructures, and uploads locally digitized packages to S3')
    parser.add_argument('spreadsheet_path', help='Path to spreadsheet containing information about packages to be processed')
    parser.add_argument('-r', '--restricted_batch', action=argparse.BooleanOptionalAction, help='Boolean indicating if the batch is restricted or not.', default=False)
    args = parser.parse_args()
    main(args.spreadsheet_path, args.restricted_batch)