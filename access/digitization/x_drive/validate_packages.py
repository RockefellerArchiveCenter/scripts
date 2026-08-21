#!/usr/bin/env python3

# Activate environment
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
        current_path = row['current_path'].strip()
        package_id = current_path.split("/")[-1]
        if "Backlog_Project" in current_path:
            package_path = Path(current_path, 'data')
        else:
            package_path = Path(current_path)
        try:
            assert package_path.is_dir(), f"Package does not exist at {package_path}"
            assets, asset_errors = validate_assets(package_path, package_id)
            # file_formats, file_format_error = validate_file_formats(package_path)
            ocr, ocr_errors = validate_ocr(package_path, package_id)
        except Exception as e:
            print(e)
            
        if not all([assets, ocr]):
            all_errors = list(set([e for e in asset_errors if bool(e)] + [e for e in ocr_errors if bool(e)]))
            formatted_errors = "; ".join(all_errors)
            print(f"{package_path}\t{formatted_errors}")

def validate_directories(bag_path):
    """Checks for the presence of expected directories.

    Args:
        bag_path (pathlib.Path): path of bagit Bag containing assets.

    Raises:
        FileNotFoundError if not all directories are present.
    """
    master_path = bag_path / 'master'
    master_edited_path = bag_path / 'master_edited'
    if master_edited_path.is_dir() and not master_path.is_dir():
        print(f"mv {master_edited_path} {master_path}")
    missing_dirs = []
    for dir in ['master', 'service_edited']: # TODO removed master_edited
        if not (bag_path / dir).is_dir():
            missing_dirs.append(dir)
    if len(missing_dirs):
        return False, f"Expected directories missing: {', '.join(missing_dirs)}"
    return True, None

def validate_service_edited_count(bag_path):
    dir = bag_path / 'service_edited'
    count = len(list(dir.rglob('*')))
    if count != 1:
        return False, f"Expected 1 file in service_edited dir, got {count}"
    return True, None

def validate_file_counts(bag_path, transaction_number):
    """Asserts correct number of files is present in each directory."""
    pdf_path = bag_path / 'service_edited' / f'{transaction_number}.pdf'
    if not pdf_path.exists():
        return False, f"PDF does not exist at {pdf_path}"
    with pymupdf.open(bag_path / 'service_edited' / f'{transaction_number}.pdf', filetype='pdf') as document:
        pdf_page_count = document.page_count
    master_file_count = len(list((bag_path / 'master').glob('*.tif')))
    master_edited_file_count = len(list((bag_path / 'master_edited').glob('*.tif')))
    if bool(master_edited_file_count) and (pdf_page_count != master_edited_file_count):
        return False, f"PDF has {pdf_page_count} pages but found {master_edited_file_count} files in master_edited directory"
    if master_file_count < master_edited_file_count:
        return False, f"{master_edited_file_count} files found in master_edited directory but only {master_file_count} in master directory"
    if master_edited_file_count == 0 and master_file_count == 0:
        return False, "No TIFF files were found in expected directories."
    return True, None

def validate_file_names(bag_path):
    """Ensures file names are valid.

    Args:
        bag_path (pathlib.Path): path of bagit Bag containing assets.
    """
    for dir in ['master', 'master_edited', 'service_edited']:
        if (bag_path / dir).is_dir():
            for fp in (bag_path / dir).iterdir():
                if " " in fp.name:
                    return False, f"File name {str(fp)} contains space."
    return True, None

def validate_ocr(bag_path, transaction_number):
    """Ensures there is an OCR layer for each page of the PDF.

    Args:
        bag_path (pathlib.Path): path of bagit Bag containing assets.
        transaction_number (str): transaction number of package.
    """
    pdf_path = bag_path / 'service_edited' / f'{transaction_number}.pdf'
    if not pdf_path.exists():
        return False, [f"PDF does not exist at {pdf_path}"]
    with pymupdf.open(pdf_path, filetype='pdf') as document:
        for page in document:
            if page.get_text("text"):
                return True, []
    return False, [f'No OCR detected in package {transaction_number}']

def validate_assets(bag_path, transaction_number):
    """Ensures that all expected directories and files are present.

    Args:
        bag_path (pathlib.Path): path of bagit Bag containing assets.

    Raises:
        AssetValidationError if files delivered do not match expected files.
    """
    directories, directories_message = validate_directories(bag_path)
    pdf_count, pdf_count_message = validate_service_edited_count(bag_path)
    file_counts, file_counts_messages = validate_file_counts(bag_path, transaction_number)
    file_names, file_names_message = validate_file_names(bag_path)
    if not all([directories, pdf_count, file_counts, file_names]):
        return False, [directories_message, pdf_count_message, file_counts_messages, file_names_message]
    return True, []

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
            print(fp)
            try:
                validate_file_characteristics(fp)
            except AssertionError as e:
                return False, f"TIFF file does not meet specs: {e}"
            except Exception as e:
                return False, f"Invalid TIFF file {str(fp)}: {e}"
    return True, None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Validates, restructures, and uploads locally digitized packages to S3')
    parser.add_argument('spreadsheet_path', help='Path to spreadsheet containing information about packages to be processed')
    args = parser.parse_args()
    main(args.spreadsheet_path)