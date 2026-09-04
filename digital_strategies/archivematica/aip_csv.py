#!/usr/bin/python

# Creates a CSV of all AIPs in the Storage Service.

import csv
from amclient import AMClient

STORAGE_SERVICE_API_KEY = ""
STORAGE_SERVICE_USER_NAME = ""
STORAGE_SERVICE_URL = ""


def main():
    archivematica_client = AMClient(
            ss_api_key=STORAGE_SERVICE_API_KEY,
            ss_user_name=STORAGE_SERVICE_USER_NAME,
            ss_url=STORAGE_SERVICE_URL)
    with open('aips.csv', 'w', newline='') as csvfile:
        fieldnames = ['uuid', 'current_location', 'origin_pipeline', 'status']
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()

        for aip in archivematica_client.aips():
            writer.writerow(aip)


if __name__ == '__main__':
    main()