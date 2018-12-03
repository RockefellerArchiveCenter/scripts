#!/usr/bin/env python

import base64
import json
from os.path import join
import requests
import time

# list of directory names you want to start and approve.
# These all need to be in the transfer source location indicated below
transfers = [
    ''
]

username = 'user' # dashboard username
apikey = 'apikey' # api key for dashboard user
headers = {"Authorization": "ApiKey {}:{}".format(username, apikey)}
baseurl = 'dashboard-ip'
location_uuid = 'location-uuid' # UUID for transfer source

for txfr in transfers:
    time.sleep(60) # pause for 1 minute
    print("Starting {}".format(txfr) + time.strftime(" %b %d %H:%M:%S"))
    basepath = "/mnt/nfs-archivematica/staging/{}".format(txfr)
    full_url = join(baseurl, 'transfer/start_transfer/')
    bagpaths = "{}:{}".format(location_uuid, basepath)
    params = {'name': txfr, 'type': 'standard',
              'paths[]': base64.b64encode(bagpaths.encode())}
    # start transfer: https://wiki.archivematica.org/Archivematica_API#Start_Transfer
    start = requests.post(full_url, headers=headers, data=params)
    print(start.json()['message'] + time.strftime(" %b %d %H:%M:%S"))
    time.sleep(30) # pause for 30 seconds
    print("Approving {}".format(txfr) + time.strftime(" %b %d %H:%M:%S"))
    time.sleep(30) # pause for 30 seconds
    approve_transfer = requests.post(join(baseurl, 'transfer/approve_transfer/'),
                                     headers=headers,
                                     data={'type': 'standard', 'directory': txfr})
    print(approve_transfer.json()['message']  + time.strftime(" %b %d %H:%M:%S"))
    time.sleep(600) # pause for 10 minutes
