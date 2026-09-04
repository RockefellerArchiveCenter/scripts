#!/usr/bin/python

import argparse
from amclient import AMClient

STORAGE_SERVICE_API_KEY = ""
STORAGE_SERVICE_USER_NAME = ""
STORAGE_SERVICE_URL = ""


def main(aip_uuid, pipeline_uuid, processing_config, reingest_type):
    client = AMClient(
            ss_api_key=STORAGE_SERVICE_API_KEY,
            ss_user_name=STORAGE_SERVICE_USER_NAME,
            ss_url=STORAGE_SERVICE_URL)
    client.aip_uuid = aip_uuid
    client.pipeline_uuid = pipeline_uuid
    client.processing_config = processing_config
    client.reingest_type = reingest_type
    reingested = client.reingest_aip()
    print(reingested)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Reingest an AIP.')
    parser.add_argument('aip_uuid', help='UUID of AIP to reingest')
    parser.add_argument('pipeline_uuid', help='UUID of pipeline to use for reingest')
    parser.add_argument('-p', '--processing_config', default='default', help='Processing config to use for reingest.')
    parser.add_argument('-t', '--type', default='OBJECTS', choices=['METADATA_ONLY', 'OBJECTS', 'FULL'], help='Type of reingest to perform')
    args = parser.parse_args()
    main(args.aip_uuid, args.pipeline_uuid, args.processing_config, args.type)