#!/usr/bin/env python3

# Pre-run requirements
# Get on RAC network
# Connect to X drive
# Update AWS session credentials

import argparse
import tarfile
from datetime import datetime
from pathlib import Path
from shutil import rmtree, copytree

import bagit
import boto3
import pandas
import pymupdf
from PIL import Image

AWS_ROLE_NAME = "avdev"
AWS_BUCKET_NAME = "test"

RESTRICTED_DIR = "RESTRICTED"
UPLOADED_DIR = "UPLOADED"
INVALID_DIR = "INVALID"


def main(spreadsheet_path, restricted):
    """Main method which calls all other submethods."""
    
    aws_session = boto3.Session(profile_name=AWS_ROLE_NAME) # TODO this will likely need to be changed
    s3_client = aws_session.client('s3')

    df = pandas.read_excel(spreadsheet_path, header=0)
    for index, row in df.iterrows():
        refid = row['refid'].strip()
        package_path = Path(row['current_path'].strip())
        assert package_path.is_dir(), f"Package does not exist at {package_path}"

        remove_unwanted_files(package_path)

        if is_valid_package(package_path):
            renamed_path = rename_files(package_path, refid)
            if restricted:
                move_to_dir(renamed_path, RESTRICTED_DIR)
            else:
                bagit.make_bag(str(renamed_path))
                tarball_path = create_tarball(renamed_path)
                upload_package(tarball_path, s3_client)
                Path(UPLOADED_DIR).mkdir(exist_ok=True)
                tarball_path.rename(Path(UPLOADED_DIR, tarball_path.name))
        else:
            renamed_path = rename_files(package_path, refid)
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
    rights_statements = aquila_client.get_rights_data(
        rights_ids, 
        datetime.strftime(start_date, "%Y-%m-%d"), 
        datetime.strftime(end_date, "%Y-%m-%d"))
    for rights_statement in rights_statements:
        for granted in get_active_rights_acts(rights_statement['rights_granted']):
            if granted['act'] in ['publish', 'disseminate'] and granted['grant_restriction'] != 'allow':
                return True
    return False

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

def is_valid_package(dir_path):
    """Validates package structure and assets.
    
    Args:
        dir_path (pathlib.Path): path of digitized object to validate.
    """
    try:
        validate_assets(dir_path, dir_path.stem)
        validate_file_formats(dir_path)
        validate_ocr(dir_path, dir_path.stem)
        return True
    except Exception as e:
        print(e)
        return False


def validate_directories(bag_path):
    """Checks for the presence of expected directories.

    Args:
        bag_path (pathlib.Path): path of bagit Bag containing assets.

    Raises:
        FileNotFoundError if not all directories are present.
    """
    for dir in ['master', 'master_edited', 'service_edited']:
        if not (bag_path / dir).is_dir():
            raise FileNotFoundError(f"Expected directory {dir} is missing")

def validate_file_counts(bag_path, current_dir):
    """Asserts correct number of files is present in each directory."""
    with pymupdf.open(bag_path / 'service_edited' / f'{current_dir}.pdf', filetype='pdf') as document:
        pdf_page_count = document.page_count
    master_file_count = len(list((bag_path / 'master').glob(f'{current_dir}*.tif')))
    master_edited_file_count = len(
        list((bag_path / 'master_edited').glob(f'{current_dir}*.tif')))
    if pdf_page_count != master_edited_file_count:
        raise Exception(
            f"PDF has {pdf_page_count} pages but found {master_edited_file_count} files in master_edited directory")
    if master_file_count < master_edited_file_count:
        raise Exception(
            f"{master_edited_file_count} files found in master_edited directory but only {master_file_count} in master directory")

def validate_file_names(bag_path):
    """Ensures file names are valid.

    Args:
        bag_path (pathlib.Path): path of bagit Bag containing assets.
    """
    for dir in ['master', 'master_edited', 'service_edited']:
        for fp in (bag_path / dir).iterdir():
            if " " in fp.name:
                raise Exception(f"File name {str(fp)} contains space.")

def validate_ocr(bag_path, current_dir):
    """Ensures there is an OCR layer for each page of the PDF.

    Args:
        bag_path (pathlib.Path): path of bagit Bag containing assets.
    """
    with pymupdf.open(bag_path / 'service_edited' / f'{current_dir}.pdf', filetype='pdf') as document:
        for page in document:
            if page.get_text("text"):
                return True
    raise Exception(f'No OCR detected in package {current_dir}')

def validate_assets(bag_path, current_dir):
    """Ensures that all expected directories and files are present.

    Args:
        bag_path (pathlib.Path): path of bagit Bag containing assets.

    Raises:
        AssetValidationError if files delivered do not match expected files.
    """
    try:
        validate_directories(bag_path)
        validate_file_counts(bag_path, current_dir)
        validate_file_names(bag_path)
    except Exception as e:
        raise Exception(
            f"Package structure is invalid: {e}") from e

def validate_file_characteristics(image_path):
    with Image.open(image_path) as image:
        image.load()  # Ensures TIFF is valid
        assert image.mode in ["L", "RGB"], f"Image format should be RGB or L, got {image.mode}."
        resolution = image.info.get('dpi', image.info.get('resolution'))
        assert resolution, "Image does not have embedded resolution information."
        assert resolution[0] >= 400 and resolution[1] >= 400, f"Image resolution should be at least 400dpi, got {image.info['dpi']}"

def validate_file_formats(bag_path):
    """Ensures that files pass format validation rules.

    Args:
        bag_path (pathlib.Path): path of bagit Bag containing assets.
    """
    for dir in ['master', 'master_edited']:
        for fp in (bag_path / dir).glob('*.tif'):
            try:
                validate_file_characteristics(fp)
            except AssertionError as e:
                raise Exception(f"TIFF file does not meet specs: {e}")
            except Exception as e:
                raise Exception(f"Invalid TIFF file {str(fp)}: {e}")

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
    parser.add_argument('--restricted_batch', action=argparse.BooleanOptionalAction, help='Boolean indicating if the batch is restricted or not.', default=False)
    args = parser.parse_args()
    main(args.spreadsheet_path, args.restricted_batch)