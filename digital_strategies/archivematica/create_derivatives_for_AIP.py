#!/usr/bin/env python3

# Creates new IIIF derivatives for AIP stored in Archivematica AIP Store

import argparse
import tarfile
import shortuuid
from pathlib import Path

import bagit
import boto3
import py7zr
from shutil import rmtree, copytree
from amclient import AMClient


STORAGE_SERVICE_URL = ''
STORAGE_SERVICE_USER_NAME = ''
STORAGE_SERVICE_API_KEY = ''

PICTOR_BUCKET = 'rac-prod-iiif-upload'
PDF_BUCKET = 'raciiif-prod'


def main(aip_uuid, archivesspace_uri):
    am_client = AMClient(
            ss_api_key=STORAGE_SERVICE_API_KEY,
            ss_user_name=STORAGE_SERVICE_USER_NAME,
            ss_url=STORAGE_SERVICE_URL,
            directory='aip_reprocessing')
    print('Downloading AIP')
    download_path = am_client.download_package(aip_uuid)

    print('Extracting AIP')
    with py7zr.SevenZipFile(download_path, mode='r') as z:
        z.extractall(path='aip_reprocessing')

    extracted_path = ".".join(download_path.split(".")[:-1])
    current_path = Path('aip_reprocessing', aip_uuid)
    copytree(extracted_path, current_path)
    rmtree(extracted_path)
    print(f'AIP moved from {extracted_path} to {current_path}')

    session = boto3.Session(profile_name='avprod')
    s3_client = session.client('s3')

    pdf_path = list(current_path.rglob('*.pdf'))[0]
    dimes_id = str(shortuuid.uuid(name=archivesspace_uri))
    print("Uploading PDF")
    s3_client.upload_file(pdf_path, PDF_BUCKET, f'pdfs/{dimes_id}')

    print('Restructuring')
    restructure(current_path)
    print('Updating Bag')
    create_bag(current_path, archivesspace_uri)

    tar_path = current_path.with_suffix('.tar.gz')
    
    print('Compressing updated package')
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(current_path, arcname=aip_uuid)

    print('Uploading package')
    s3_client.upload_file(tar_path, PICTOR_BUCKET, tar_path.name)

    tar_path.unlink()
    rmtree(current_path)
    Path(download_path).unlink()

def restructure(current_path):
    copytree((current_path / 'data' / 'objects' / 'service'), (current_path / 'data' / 'service'))
    for fp in current_path.rglob('data/*'):
        if 'service' not in fp.parts:
            if fp.is_dir():
                rmtree(fp)
            else:
                fp.unlink()

def create_bag(current_path, archivesspace_uri):
    bag = bagit.Bag(str(current_path))
    bag.info['ArchivesSpace-URI'] = archivesspace_uri
    bag.save(manifests=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('aip_uuid')
    parser.add_argument('as_uri')
    args = parser.parse_args()
    main(args.aip_uuid, args.as_uri)