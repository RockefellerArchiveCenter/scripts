#!/usr/bin/env python3

# Checks that the number of packages expected matches what has been received
# Reports on mismatches between expected number of packages, packages in the embargo bucket, and PDF files
# Returns a list of packages and PDF files with page counts (where available) and last modified date

import io
import configparser
import tarfile

import boto3
import pandas
import pymupdf

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    session = boto3.Session(profile_name=config['AWS']['profile_name'])
    s3_client = session.client('s3')
    df = pandas.read_excel(config['RAC']['spreadsheet_path'], sheet_name='Reel', header=0)
    df.columns = df.columns.str.strip()
    filtered_df = df[df['Approved/Rejected'] == 'Approved']
    series = filtered_df['Filename'].value_counts()
    for refid, spreadsheet_count in (zip(series.index, series)):
        packages = s3_client.list_objects_v2(Bucket=config['AWS']['embargo_bucket_name'], Prefix=refid)
        pdfs = s3_client.list_objects_v2(Bucket=config['AWS']['embargo_pdf_bucket_name'], Prefix=refid)
        if not (spreadsheet_count == pdfs['KeyCount'] == packages['KeyCount']):
            formatted_package_data = None
            formatted_pdf_data = None
            if packages['KeyCount'] > 0:
                formatted_package_data = format_package_data(packages['Contents'], config, s3_client)
            if pdfs['KeyCount'] > 0:
                formatted_pdf_data = format_pdf_data(pdfs['Contents'], config, s3_client)
            # print(f"Refid {refid}: {spreadsheet_count} found in RAC inventory, {packages['KeyCount']} in embargo bucket, {pdfs['KeyCount']} in embargo PDF bucket")
            # if formatted_package_data:
            #     print(f"Packages in embargo bucket:\n{formatted_package_data}")
            # if formatted_pdf_data:
            #     print(f"Packages in embargo PDF bucket:\n{formatted_pdf_data}\n\n")


def format_package_data(packages, config, s3_client):
    package_list = []
    for p in packages:
        page_count = 0
        # try:
        #     data = s3_client.get_object(Bucket=config['AWS']['embargo_bucket_name'], Key=p['Key'])['Body'].read()
        #     fileobj = io.BytesIO(data)
        #     with tarfile.open(fileobj=fileobj) as tf:
        #         for n in tf.getnames():
        #             if 'master_edited' in n:
        #                 page_count += 1
        # except Exception:
        #     pass
        package_list.append(f"{p['Key']}\t{page_count}\t{p['LastModified']}")
    return "\n".join(package_list)


def format_pdf_data(pdfs, config, s3_client):
    pdf_list = []
    for p in pdfs:
        page_count = 0
        # try:
        #     resp = s3_client.get_object(Bucket=config['AWS']['embargo_pdf_bucket_name'], Key=p['Key'])
        #     body = resp['Body'].read()
        #     doc = pymupdf.open(resp['ContentType'], body)
        #     page_count = doc.page_count
        # except Exception as e:
        #     print(e)
        #     pass
        pdf_list.append(f"{p['Key']}\t{page_count}\t{p['LastModified']}")
    return "\n".join(pdf_list)


if __name__ == '__main__':
    main()