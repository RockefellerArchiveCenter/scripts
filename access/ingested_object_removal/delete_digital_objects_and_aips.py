#!/usr/bin/env python3

"""Deletes AS digital objects, Archivematica AIPs and DIPs, and Fedora files.

This script can be used when incorrect digital objects have been ingested
into Archivematica.

Expects a filepath to a CSV with a single column containing ArchivesSpace URIs
for archival objects to be processed, as well as a filepath to a config file
with the following structure:

[ArchivesSpace]
baseurl = # ArchivesSpace base URL
username = # ArchivesSpace username
password =  # ArchivesSpace password

[Archivematica]
ss_url = # Storage Service base URL
ss_user_name = # Storage Service username
ss_api_key =  # Storage Service API Key
delete_user_email = # Email of Storage Service user to 
delete_user_id = # Database ID of Storage Service user to associate delete request with (integer)

[Fedora]
baseurl = # Fedora baseurl
username = # Fedora username
password = # Fedora password
"""

import argparse
from configparser import ConfigParser
from csv import reader

from amclient import AMClient
from asnake.client import ASnakeClient
from pyfc4 import models as fcrepo

def main(csv_path, config_path):
    config = ConfigParser()
    config.read(config_path)
    as_client = ASnakeClient(
        baseurl = config['ArchivesSpace']['baseurl'],
        username = config['ArchivesSpace']['username'],
        password = config['ArchivesSpace']['password']
    )
    am_client = AMClient(
        ss_url = config['Archivematica']['ss_url'],
        ss_user_name = config['Archivematica']['ss_user_name'],
        ss_api_key = config['Archivematica']['ss_api_key'],
        delete_user_email = config['Archivematica']['delete_user_email'],
        delete_user_id = config['Archivematica']['delete_user_id'])
    fedora_client = fcrepo.Repository(
        config['Fedora']['baseurl'],
        config['Fedora']['username'], 
        config['Fedora']['password'], 
        default_serialization="application/ld+json")
    with open(csv_path, 'r') as csv_file:
        csv_reader = reader(csv_file)
        for row in csv_reader:
            if is_valid_uri(row[0]):
                try:
                    bag_identifier = delete_digital_object(row[0], as_client)
                    uuid_list = delete_am_aip(bag_identifier, am_client)
                    delete_fedora_aip(uuid_list, fedora_client)
                except Exception as e:
                    print(e, row[0])


def is_valid_uri(val):
    return bool(val.startswith('/repositories/'))


def delete_digital_object(ao_uri, client):
    """Deletes ArchivesSpace digital object.

    Args:
        ao_uri (str): URI for archival object from which digital object should be deleted.
        client (ASpace.client): ArchivesSpace client.

    Returns:
        bag_identifier (str): Identifier which can be used to find assets in other systems.
    """
    ao = client.get(ao_uri, params={'resolve[]': 'digital_object'}).json()
    digital_objects = [i for i in ao['instances'] if i['instance_type'] == 'digital_object']
    if len(digital_objects) != 1:
        raise Exception(f'Expected exactly one digital object to be attached to this archival object, got {len(digital_objects)}')
    digital_object = digital_objects[0]['digital_object']['_resolved']
    client.delete(digital_object['uri'])
    updated_ao = client.get(ao_uri).json()
    client.post(ao_uri, json=updated_ao)
    print(f"Digital object {digital_object['uri']} deleted.")
    return digital_object['digital_object_id']


def delete_am_aip(bag_identifier, am_client):
    """Deletes Archivematica AIP.
    
    Args:
        bag_identifier (str): identifier for the bag, which is the AIP name.
        am_client (AMClient): Archivematica client.

    Returns:
        aip_uuid (list of str): UUID of deleted AIP.
    """
    am_client.package_uuid = bag_identifier
    aip = am_client.get_package_details()
    am_client.delete_package(
            aip['uuid'], 
            aip['origin_pipeline'].split('/')[-2], 
            'Digitized content: PDFs do not match TIFFs', 
            am_client.delete_user_id, 
            am_client.delete_user_email)
    print(f"AIP {aip['uuid']} deleted.")
    return aip['uuid']


def delete_fedora_aip(aip_uuid, fedora_client):
    """Delete AIPs from Fedora.
    
    Args:
        aip_uuid (str): UUID of AIP to delete
        fedora_client (pyfc4.fcrepo.Repository): client to interact with Fedora
    """
    resource = fedora_client.get_resource(aip_uuid)
    resource.delete()
    print(f"Fedora resource {resource} deleted.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Delete digital objects, AIPs and DIPS')
    parser.add_argument('csv_path', help='Filepath of CSV file containing AS URIs to process.')
    parser.add_argument('config_path', help='Filepath to config file.', default='config.ini')
    args = parser.parse_args()
    main(args.csv_path, args.config_path)