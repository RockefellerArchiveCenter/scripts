#!/usr/bin/env python3

# Returns a list of packages and PDF files with page counts (where available) and last modified date

import io
import configparser
import tarfile

import boto3
import pandas
import pymupdf

REFIDS = []

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    session = boto3.Session(profile_name=config['AWS']['profile_name'])
    s3_client = session.client('s3')
    for refid in REFIDS:
        packages = s3_client.list_objects_v2(Bucket=config['AWS']['embargo_bucket_name'], Prefix=refid)
        pdfs = s3_client.list_objects_v2(Bucket=config['AWS']['embargo_pdf_bucket_name'], Prefix=refid)
        format_package_data(packages)
        format_pdf_data(pdfs)

def format_package_data(packages, config, s3_client):
    for p in packages:
        page_count = 0
        try:
            s3_client.download_file(config['AWS']['embargo_bucket_name'], p['Key'], p['Key'])
            with tarfile.open(p['Key']) as tf:
                for n in tf.getnames():
                    if 'master_edited' in n:
                        page_count += 1
            print(f"{p['Key']}\t{page_count}\t{p['LastModified']}")
        except Exception as e:
            print(e)
            pass


def format_pdf_data(pdfs, config, s3_client):
    for p in pdfs:
        page_count = 0
        try:
            s3_client.download_file(config['AWS']['embargo_pdf_bucket_name'], p['Key'], p['Key'])
            doc = pymupdf.open(p['Key'])
            page_count = doc.page_count
            print(f"{p['Key']}\t{page_count}\t{p['LastModified']}") 
        except Exception as e:
            print(e)
            pass


if __name__ == '__main__':
    main()