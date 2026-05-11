#!/usr/bin/env python3

# usage: check_package_by_status.py crowley_inventory_path cue_see_csv_path {approved,delivered}

# Confirms delivery or approval of packages.

# positional arguments:
#   crowley_inventory_path
#   cue_see_csv_path
#   {approved,delivered}

# options:
#   -h, --help            show this help message and exit
#   -d DELIVERY_DATE, --delivery_date DELIVERY_DATE

import argparse
import configparser

import boto3
import botocore
import pandas

def get_crowley_data(inventory_path):
    refid_list = []
    df = pandas.read_excel(inventory_path, header=0)
    for index, row in df.iterrows():
        refid_list.append((row['Filename'].strip(), row['Roll Number'].strip()))
    return refid_list


def get_cue_see_data(cue_see_path):
    refid_list = []
    df = pandas.read_csv(cue_see_path, header=0)
    for index, row in df.iterrows():
        reel_number = row['Original Filename'].split("/")[1]
        refid_list.append(((row['Ref ID']), reel_number))
    return refid_list


def key_exists(client, bucket, key):
    try:
        client.head_object(Bucket=bucket, Key=key)
        return True
    except client.exceptions.NoSuchKey:
        False
    except botocore.exceptions.ClientError as err:
        if err.response['Error']['Code'] == '404':
            return False


def main(crowley_inventory_path, cue_see_csv_path, status):
    config = configparser.ConfigParser()
    config.read('config.ini')
    session = boto3.Session(profile_name=config['AWS']['profile_name'])
    s3_client = session.client('s3')
    qc_error_packages = []
    embargo_error_packages = []
    embargo_pdf_error_packages = []
    errors = []

    crowley_data = get_crowley_data(crowley_inventory_path)
    cue_see_data = get_cue_see_data(cue_see_csv_path)

    for refid, reel_number in crowley_data:
        if status == 'approved':
            if (refid, reel_number) in cue_see_data:
                qc_error_packages.append((refid, reel_number))

            if not key_exists(s3_client, config['AWS']['embargo_bucket_name'], f'{refid}.tar.gz'):
                embargo_error_packages.append((refid, reel_number))
            
            if not key_exists(s3_client, config['AWS']['embargo_pdf_bucket_name'], f'{refid}.pdf'):
                embargo_pdf_error_packages.append((refid, reel_number))
        else:
            if (refid, reel_number) not in cue_see_data:
                qc_error_packages.append((refid, reel_number))
    
    if len(qc_error_packages):
        result_text = "were found in" if status == 'approved' else "were not found in"
        package_list = "\n".join([" ".join([p[0], p[1]]) for p in qc_error_packages])
        errors.append(f"The following {len(qc_error_packages)} packages (out of a total of {len(crowley_data)}) {result_text} {config['AWS']['qc_bucket_name']}:\n{package_list}")

    if len(embargo_error_packages):
        package_list = "\n".join([" ".join([p[0], p[1]]) for p in embargo_error_packages])
        errors.append(f"The following {len(embargo_error_packages)} packages (out of a total of {len(crowley_data)}) were not found in {config['AWS']['embargo_bucket_name']}:\n{package_list}")

    if len(embargo_pdf_error_packages):
        package_list = "\n".join([" ".join([p[0], p[1]]) for p in embargo_pdf_error_packages])
        errors.append(f"The following {len(embargo_pdf_error_packages)} packages (out of a total of {len(crowley_data)}) were not found in {config['AWS']['embargo_pdf_bucket_name']}:\n{package_list}")
    
    if len(errors):
        print("\n\n".join(errors))
    else:
        print(f"All {len(crowley_data)} packages have been {status}.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Confirms delivery or approval of packages.')
    parser.add_argument('crowley_inventory_path')
    parser.add_argument('cue_see_csv_path')
    parser.add_argument('status', choices=['approved', 'delivered'])
    args = parser.parse_args()
    main(args.crowley_inventory_path, args.cue_see_csv_path, args.status)