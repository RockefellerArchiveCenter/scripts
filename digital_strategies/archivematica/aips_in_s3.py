#!/usr/bin/env python3

# Check to see if AIP in AMSS actually exists in storage location

import boto3
from amclient import AMClient

S3_BUCKET = 'rac-prod-amss-born-digital'
LOCATION_UUID = '8aae69cc-a471-40cb-b694-448c9dbc07b1'
AWS_SESSION_NAME = ''

STORAGE_SERVICE_URL = 'http://archivematica-storage-service.rockarch.org:8000'
STORAGE_SERVICE_USER_NAME = ''
STORAGE_SERVICE_API_KEY = ''

def main():
    am_client = AMClient(
        ss_api_key=STORAGE_SERVICE_API_KEY,
        ss_user_name=STORAGE_SERVICE_USER_NAME,
        ss_url=STORAGE_SERVICE_URL,
        directory='aip_reprocessing')
    aws_session = boto3.Session(profile_name=AWS_SESSION_NAME)
    aws_client = aws_session.client('s3')
    for aip in am_client.aips():
        if LOCATION_UUID in aip['current_location']:
            try:
                aws_client.head_object(
                    Bucket=S3_BUCKET,
                    Key=aip['current_full_path'])
            except Exception as e:
                print(e, aip['uuid'])

if __name__ == '__main__':
    main()