#!/usr/bin/env python

import base64
import json
import requests
import time
import os

# list of directory names you want to start and approve.
# These all need to be in the transfer source location indicated below
transfers = [
    ''
]

username = 'user' # dashboard username
apikey = 'apikey' # api key for dashboard user
headers = {"Authorization": "ApiKey {}:{}".format(username, apikey)}
baseurl = 'http://dashboard-ip/api'
location_uuid = 'location-uuid' # UUID for transfer source

wait_time = 5 # number of seconds to pause before pinging API in loops

for txfr in transfers:
    print("Starting {}".format(txfr) + time.strftime(" %b %d %H:%M:%S"))
    basepath = "/mnt/nfs-archivematica/staging/{}".format(txfr)
    full_url = join(baseurl, 'transfer/start_transfer/')
    bagpaths = "{}:{}".format(location_uuid, basepath)
    params = {'name': txfr, 'type': 'standard',
              'paths[]': base64.b64encode(bagpaths.encode())}
    # start transfer: https://wiki.archivematica.org/Archivematica_API#Start_Transfer
    start = requests.post(full_url, headers=headers, data=params)
    print(start.json()['message'] + time.strftime(" %b %d %H:%M:%S"))
    time.sleep(5)
    print("Approving {}".format(txfr) + time.strftime(" %b %d %H:%M:%S"))
    while True:
        unapproved_transfers = requests.get(os.path.join(baseurl, 'transfer/unapproved'), headers=headers).json().get('results')
        if unapproved_transfers and txfr in str(unapproved_transfers):
            transferUuid = unapproved_transfers[0].get('uuid')
            break
        else:
            print("No transfers awaiting approval")
            time.sleep(wait_time)
    approve_transfer = requests.post(join(baseurl, 'transfer/approve_transfer/'),
                                     headers=headers,
                                     data={'type': 'standard', 'directory': txfr})
    print(approve_transfer.json()['message']  + time.strftime(" %b %d %H:%M:%S"))
    transferStatusUrl = join(baseurl, 'transfer/status/', transferUuid)
    time.sleep(120)
    while True:
        transferStatus = requests.get(transferStatusUrl, headers=headers).json().get('status')
        if transferStatus == 'COMPLETE':
            print("Transfer complete!")
            sipUuid = requests.get(transferStatusUrl, headers=headers).json().get('sip_uuid')
            ingestStatusUrl = join(baseurl, 'ingest/status/', sipUuid)
            time.sleep(180)
            while True:
                ingestStatus = requests.get(ingestStatusUrl, headers=headers).json().get('status')
                if ingestStatus == 'COMPLETE':
                    break
                elif ingestStatus == 'FAILED':
                    print(txfr + " failed during ingest!")
                    break
                time.sleep(wait_time)
            break
        elif transferStatus == 'FAILED':
            print(txfr + " failed during transfer!")
            break
        time.sleep(wait_time)
