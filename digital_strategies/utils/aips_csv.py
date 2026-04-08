#!/usr/bin/python

# This script generates a CSV file of all AIPs, with columns for location, origin pipeline, and status.

import csv
from amclient import AMClient

SS_API_KEY = ""
SS_USER_NAME = ""
SS_URL = "http://archivematica-storage-service.dev.rockarch.org:8000/"


def main():
    archivematica_client = AMClient(
            ss_api_key=SS_API_KEY,
            ss_user_name=SS_USER_NAME,
            ss_url=SS_URL)
    with open('aips.csv', 'w', newline='') as csvfile:
        fieldnames = ['uuid', 'current_location', 'origin_pipeline', 'status']
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()

        for aip in archivematica_client.aips():
            writer.writerow(aip)


if __name__ == '__main__':
    main()