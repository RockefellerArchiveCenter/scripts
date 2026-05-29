#!/usr/bin/env python3

# usage: check_dupe_delivery.py [-h] approval_date refids [refids ...]

# Confirms delivery or approval of duplicate packages.

# positional arguments:
#   approval_date
#   refids

# options:
#   -h, --help     show this help message and exit

import argparse
import configparser
from datetime import datetime, timezone
from datetime import timedelta

import boto3


def key_exists(client, bucket, refid, approval_date, max_modified_date):
    dupes = []
    matching = client.list_objects_v2(Bucket=bucket, Prefix=refid)
    for m in matching['Contents']:
        if (approval_date < m['LastModified'] < max_modified_date):
            dupes.append(m)
    if len(dupes) != 1:
        return False
    return True

def main(approval_date, refids):
    config = configparser.ConfigParser()
    config.read('config.ini')
    session = boto3.Session(profile_name=config['AWS']['profile_name'])
    s3_client = session.client('s3')
    embargo_error_packages = []
    embargo_pdf_error_packages = []
    errors = []

    parsed_approval_date = approval_date.replace(tzinfo=timezone.utc)
    max_modified_date = parsed_approval_date + timedelta(hours=48)

    for r in refids:
        if not key_exists(s3_client, config['AWS']['embargo_bucket_name'], r, parsed_approval_date, max_modified_date):
            embargo_error_packages.append(r)
        
        if not key_exists(s3_client, config['AWS']['embargo_pdf_bucket_name'], r, parsed_approval_date, max_modified_date):
            embargo_pdf_error_packages.append(r)

    if len(embargo_error_packages):
        package_list = "\n".join(embargo_error_packages)
        errors.append(f"The following {len(embargo_error_packages)} dupe packages did not have exactly one match:\n{package_list}")

    if len(embargo_pdf_error_packages):
        package_list = "\n".join(embargo_pdf_error_packages)
        errors.append(f"The following {len(embargo_pdf_error_packages)} dupe packages did not have exactly one match:\n{package_list}")
    
    if len(errors):
        print("\n\n".join(errors))
    else:
        print(f"All {len(refids)} dupe packages have been delivered.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Confirms delivery or approval of duplicate packages.')
    parser.add_argument('approval_date', type=datetime.fromisoformat)
    parser.add_argument('refids', nargs="+")
    args = parser.parse_args()
    main(args.approval_date, args.refids)