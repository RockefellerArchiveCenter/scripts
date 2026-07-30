#!/usr/bin/env python3

# Pre-run requirements
# Get on RAC network
# Connect to X drive

import argparse

from pathlib import Path

import pandas
import pymupdf
from PIL import Image


def main(spreadsheet_path):
    """Main method which calls all other submethods."""

    df = pandas.read_excel(spreadsheet_path, header=0)
    for index, row in df.iterrows():
        package_path = Path(row['current_path'].strip())

        try:
            assert package_path.is_dir(), f"Package does not exist at {package_path}"
            validate_assets(package_path, package_path.stem)
            validate_file_formats(package_path)
            validate_ocr(package_path, package_path.stem)
            print(f"{package_path} is valid")
        except Exception as e:
            print(e)

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

def validate_file_counts(bag_path, transaction_number):
    """Asserts correct number of files is present in each directory."""
    with pymupdf.open(bag_path / 'service_edited' / f'{transaction_number}.pdf', filetype='pdf') as document:
        pdf_page_count = document.page_count
    master_file_count = len(list((bag_path / 'master').glob('*.tif')))
    master_edited_file_count = len(
        list((bag_path / 'master_edited').glob('*.tif')))
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

def validate_ocr(bag_path, transaction_number):
    """Ensures there is an OCR layer for each page of the PDF.

    Args:
        bag_path (pathlib.Path): path of bagit Bag containing assets.
        transaction_number (str): transaction number of package.
    """
    with pymupdf.open(bag_path / 'service_edited' / f'{transaction_number}.pdf', filetype='pdf') as document:
        for page in document:
            if page.get_text("text"):
                return True
    raise Exception(f'No OCR detected in package {transaction_number}')

def validate_assets(bag_path, transaction_number):
    """Ensures that all expected directories and files are present.

    Args:
        bag_path (pathlib.Path): path of bagit Bag containing assets.

    Raises:
        AssetValidationError if files delivered do not match expected files.
    """
    try:
        validate_directories(bag_path)
        validate_file_counts(bag_path, transaction_number)
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Validates, restructures, and uploads locally digitized packages to S3')
    parser.add_argument('spreadsheet_path', help='Path to spreadsheet containing information about packages to be processed')
    args = parser.parse_args()
    main(args.spreadsheet_path)