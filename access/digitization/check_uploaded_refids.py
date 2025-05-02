#!/usr/bin/env python3

import shortuuid
from asnake.aspace import ASpace
from requests import Session

refids = []

def main():
    client = ASpace().client
    http = Session()
    for refid in refids:
        resp = client.get(f'/repositories/2/find_by_id/archival_objects?ref_id[]={refid}')
        resp.raise_for_status()
        resp_data = resp.json()
        if len(resp_data['archival_objects']) != 1:
            raise Exception(f'Got wrong number of results for refid {refid}')
        ao_uri = resp_data['archival_objects'][0]['ref']
        ao_data = client.get(ao_uri).json()
        digital_objects = [i for i in ao_data['instances'] if i['instance_type'] == 'digital_object']
        for i in digital_objects:
            do_data = client.get(i['digital_object']['ref']).json()
            print(do_data['digital_object_id'])
        if len(digital_objects) < 1:
            print(f"No digital object attached to archival object with refid {refid}")
        
        dimes_id = shortuuid.uuid(name=ao_uri)
        dimes_obj = http.get(f"https://api.rockarch.org/objects/{dimes_id}").json()
        print(f"https://dimes.rockarch.org/objects/{dimes_id}/view")
        if len(dimes_obj.get('files', [])) < 1:
            print(f"No digital object available on DIMES for object with identifier {dimes_id} and refid {refid}")

if __name__ =='__main__':
    main()