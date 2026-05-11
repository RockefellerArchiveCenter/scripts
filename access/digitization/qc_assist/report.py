#!/usr/bin/env python3

import argparse
import configparser
import datetime

import boto3

TOTAL_GRANTS = 45400

# Report on number of terabytes, packages and grants received in date range.


def within_date_range(test_datetime, start_date, end_date):
    test_date = test_datetime.date()
    if end_date:
        return bool(start_date <= test_date <= end_date)
    else:
        return bool(start_date <= test_date)

def main(start_date, end_date):
    config = configparser.ConfigParser()
    config.read('config.ini')
    session = boto3.Session(profile_name=config['AWS']['profile_name'])
    s3_client = session.client('s3')
    total_bytes = 0
    package_ids = []

    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=config['AWS']['embargo_bucket_name'])
    for page in pages:
        for obj in page.get('Contents', []):
            if within_date_range(obj['LastModified'], start_date, end_date):
                total_bytes += obj['Size']
                package_ids.append(obj['Key'].split('.')[0])

    total_tb = total_bytes / (1024**4)
    total_packages = len(package_ids)
    total_grants = len(set([p.split('_')[0] for p in package_ids]))

    print(f"Total TB: {total_tb}\nTotal packages: {total_packages}\nTotal grants: {total_grants}\n")

    grants_remaining = TOTAL_GRANTS - total_grants
    size_per_grant = (total_tb / total_grants) * 1024
    tb_remaining = grants_remaining * (size_per_grant / 1024)

    print(f"Grants remaining: {grants_remaining}\nTB remaining (at {size_per_grant} GB each): {tb_remaining}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Report on number of terabytes, packages and grants received in date range.')
    parser.add_argument('start_date', type=datetime.date.fromisoformat)
    parser.add_argument('--end-date', '-e', type=datetime.date.fromisoformat)
    args = parser.parse_args()
    main(args.start_date, args.end_date)