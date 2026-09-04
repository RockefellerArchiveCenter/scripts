#!/usr/bin/env python3

# Iterates through digital objects in ArchivesSpace and checks whether AIPs exist in Archivematica

from amclient import AMClient
from asnake.aspace import ASpace

STORAGE_SERVICE_URL = ''
STORAGE_SERVICE_USER_NAME = ''
STORAGE_SERVICE_API_KEY = ''


def get_aip_uuid(digital_object):
    """Parses AIP UUID from digital object."""
    use_statement = [d for d in digital_object['file_versions'] if d['use_statement'] == 'aip'][0]
    uuid = use_statement['file_uri'].split('/')[-2]
    return uuid
    

def main():
    as_client = ASpace().client
    am_client = AMClient(
            ss_api_key=STORAGE_SERVICE_API_KEY,
            ss_user_name=STORAGE_SERVICE_USER_NAME,
            ss_url=STORAGE_SERVICE_URL)

    for digital_object in as_client.get_paged('/repositories/2/digital_objects?all_ids=true'):
        print(digital_object['uri'])
        try:
            aip_uuid = get_aip_uuid(digital_object)
            am_client.package_uuid = aip_uuid
            data = am_client.get_package_details()
            if type(data) == int:
                raise Exception(f'Could not get package details for {aip_uuid} from Archivematica')

        except Exception as e:
            print(e)

if __name__ == '__main__':
    main()