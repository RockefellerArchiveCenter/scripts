#!/usr/bin/env python

# Removes pages from packages of digitized records
# Created for use with microfilm digitization where some rolls begin or end with administrative images

import tarfile
from pathlib import Path

import boto3
import pymupdf

TO_REMOVE = [
    ("page_test", 3, 5)
]

BASE_DIR = Path('/tmp_dir')
BUCKET_NAME = 'rac-dev-image-qc'

def remove_pages(refid, delete_before, delete_after):
    if delete_after:
        remove_tiff_files('after', refid, 'master', delete_after)
        remove_tiff_files('after', refid, 'master_edited', delete_after)
        remove_pdf_pages('after', refid, delete_after)
    if delete_before:
        remove_tiff_files('before', refid, 'master', delete_before)
        renumber_tiff_files(refid, 'master')
        remove_tiff_files('before', refid, 'master_edited', delete_before)
        renumber_tiff_files(refid, 'master_edited')
        remove_pdf_pages('before', refid, delete_before)


def remove_tiff_files(operation, refid, dir_name, page):
    """Removes all TIFF files from a directory up to and including a given page number."""
    for fp in (BASE_DIR / refid / dir_name).glob('*.tif'):
        if operation == 'before':
            if int(fp.stem.split("_")[-1]) <= page:
                print(f"Deleting {fp}")
                fp.unlink()
        elif operation == 'after':
            if int(fp.stem.split("_")[-1]) >= page:
                print(f"Deleting {fp}")
                fp.unlink()


def renumber_tiff_files(refid, dir_name):
    """Renumbers TIFF files starting at page 1"""
    path_list = list((BASE_DIR / refid / dir_name).glob('*.tif'))
    sorted_paths = sorted(path_list, key=lambda p: p.name)
    iterator = 1
    for fp in sorted_paths:
        new_stem = f'{refid}_{str(iterator).zfill(4)}'
        new_path = fp.with_stem(new_stem)
        fp.rename(new_path)
        iterator += 1


def remove_pdf_pages(operation, refid, page):
    """Removes pages from a PDF file."""
    pdf_path = BASE_DIR / refid / 'service_edited' / f'{refid}.pdf'
    doc = pymupdf.open(pdf_path)
    page_count = doc.page_count
    if operation == 'before':
        doc.delete_pages(from_page=0, to_page=page-1)
    elif operation == 'after':
        doc.delete_pages(from_page=page-1, to_page=page_count-1)
    doc.saveIncr()


if __name__ == '__main__':
    s3_client = boto3.client('s3')
    for refid, delete_before, delete_after in TO_REMOVE:
        object_key = f'{refid}.tar.gz'
        local_path = BASE_DIR / object_key

        s3_client.download_file(BUCKET_NAME, object_key, local_path)
        with tarfile.open(local_path, 'r') as tarfile:
            tarfile.extractall(path=BASE_DIR)
        local_path.unlink()
        
        remove_pages(refid, delete_before, delete_after)
        
        with tarfile.open(object_key, 'w:gz') as new_tar:
            new_tar.add(Path(BASE_DIR, refid), arcname=refid)
        s3_client.upload_file(local_path, BUCKET_NAME, object_key)