#!/usr/bin/env python3

# usage: check_dupe_delivery.py [-h] approval_start_date approval_end_date reel_start reel_end

# Confirms delivery or approval of duplicate packages.

# positional arguments:
#   approval_start_date
#   approval_end_date
#   reel_start
#   reel_end

# options:
#   -h, --help     show this help message and exit

import argparse
import configparser
import pandas
from datetime import datetime, timezone

import boto3


def get_reel_list(start_reel, end_reel):
    reel_list = []
    for x in range(start_reel, end_reel+1):
        reel_list.append(f"R{x}")
    return reel_list


def packages_in_bucket(client, bucket, refid, start_date, end_date):
    packages = 0
    start_datetime = start_date.replace(tzinfo=timezone.utc)
    end_datetime = end_date.replace(tzinfo=timezone.utc)
    matching = client.list_objects_v2(Bucket=bucket, Prefix=refid)
    for m in matching.get('Contents', []):
        if (start_datetime <= m['LastModified'] <= end_datetime):
            packages += 1
    return packages

def get_rac_data(config, reel_list, start_date, end_date):
    """Return iterable of iterables with refid, grant_number, reel"""
    data = []
    df = pandas.read_excel(config['RAC']['spreadsheet_path'], sheet_name='Reel', header=0)
    df.columns = df.columns.str.strip()
    for index, row in df.iterrows():
        row_reel = str(row['Box']).strip()
        date_reviewed = row['Date Reviewed']
        if str(date_reviewed) != 'nan':
            if str(row_reel) in reel_list and (start_date <= date_reviewed <= end_date):
                data.append((row.get('Filename', '').strip(), row_reel))
    return data

def main(approval_start_date, approval_end_date, reel_start, reel_end):
    config = configparser.ConfigParser()
    config.read('config.ini')
    session = boto3.Session(profile_name=config['AWS']['profile_name'])
    s3_client = session.client('s3')
    embargo_error_packages = []
    embargo_pdf_error_packages = []
    errors = []

    reel_list = get_reel_list(reel_start, reel_end)
    rac_refids_on_reels = get_rac_data(config, reel_list, approval_start_date, approval_end_date)

    for reel in reel_list:
        reel_refids = list(set([r for r in rac_refids_on_reels if r[1] == reel]))
        for refid, reel_number in reel_refids:
            rac_package_count = len([r for r in rac_refids_on_reels if r[0] == refid])
            s3_package_count = packages_in_bucket(
                s3_client, 
                config['AWS']['embargo_bucket_name'],
                refid,
                approval_start_date,
                approval_end_date)
            s3_pdf_count = packages_in_bucket(
                s3_client, 
                config['AWS']['embargo_pdf_bucket_name'],
                refid,
                approval_start_date,
                approval_end_date)

            if rac_package_count != s3_package_count:
                embargo_error_packages.append(f"{refid} (expected {rac_package_count}, found {s3_package_count} in bucket)")
            
            if rac_package_count != s3_pdf_count:
                embargo_pdf_error_packages.append(f"{refid} (expected {rac_package_count}, found {s3_pdf_count} in bucket)")

    if len(embargo_error_packages):
        package_list = "\n".join(list(set(embargo_error_packages)))
        errors.append(f"The following approved packages in {config['AWS']['embargo_bucket_name']} did not match the expected number:\n{package_list}")

    if len(embargo_pdf_error_packages):
        package_list = "\n".join(list(set(embargo_pdf_error_packages)))
        errors.append(f"The following approved packages in {config['AWS']['embargo_pdf_bucket_name']} did not match the expected number:\n{package_list}")
    
    if len(errors):
        print("\n\n".join(errors))
    else:
        print(f"All dupe packages for reels {', '.join(reel_list)} approved between {approval_start_date} and {approval_end_date} have been delivered.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Confirms delivery or approval of duplicate packages.')
    parser.add_argument('approval_start_date', type=datetime.fromisoformat)
    parser.add_argument('approval_end_date', type=datetime.fromisoformat)
    parser.add_argument('reel_start', type=int)
    parser.add_argument('reel_end', type=int)
    args = parser.parse_args()
    main(args.approval_start_date, args.approval_end_date, args.reel_start, args.reel_end)