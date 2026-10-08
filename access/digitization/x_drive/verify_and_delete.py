#!/usr/bin/env python3

"""
Verifies that packages have been uploaded to DIMES and then deletes
uploaded packages from their current location on local storage.
"""

from pathlib import Path

import shortuuid
from asnake.aspace import ASpace
from requests import Session

UPLOADED_DIR = '/Volumes/data1/Digital_Records/Digitization/uploaded'

def main():
    as_client = ASpace().client
    http = Session()

    for refid_path in Path(UPLOADED_DIR).iterdir():
        try:
            refid = refid_path.stem
            resp = as_client.get(f'/repositories/2/find_by_id/archival_objects?ref_id[]={refid}')
            resp.raise_for_status()
            resp_data = resp.json()
            if len(resp_data['archival_objects']) != 1:
                raise Exception(f'Got wrong number of results for refid {refid}')
            ao_uri = resp_data['archival_objects'][0]['ref']
            ao_data = as_client.get(ao_uri).json()
            
            digital_objects = [i for i in ao_data['instances'] if i['instance_type'] == 'digital_object']            
            if len(digital_objects) < 1:
                raise Exception(f"No digital object attached to archival object with refid {refid}")
            
            dimes_id = shortuuid.uuid(name=ao_uri)
            dimes_obj = http.get(f"https://api.rockarch.org/objects/{dimes_id}").json()
            if len(dimes_obj.get('files', [])) < 1:
                raise Exception(f"No digital object available on DIMES for object with identifier {dimes_id} and refid {refid}")

            refid_path.unlink()
        except Exception as e:
            print(e)
            pass