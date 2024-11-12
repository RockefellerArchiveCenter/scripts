#!/usr/bin/env python3

"""
Using DIP information from Archivematica, adds digital object to file-level
children of a series for the first x number of folders in that series in
ArchivesSpace. Assumes that all file-level components that do not already
have a linked DAO should have a DAO added.
"""

import argparse
from os.path import join

from amclient import AMClient
from asnake.aspace import ASpace

config = ConfigParser()
config.read("local_settings.cfg")

parser = argparse.ArgumentParser(
    description="Using DIP information from Archivematica, adds DAOs to file-level children of a series in ArchivesSpace")
parser.add_argument(
    'resource', help='ArchivesSpace ID of resource. Example: 123')
parser.add_argument('series', help='ArchivesSpace ID of series. Example: 4321')
parser.add_argument(
    'project_name', help='Collection or other name expected to be part of SIP name. Example: Village_Green_Preservation_Society')
parser.add_argument(
    'folder_end', help='assumes "Folder" is in DIP name, folder # to stop at. Must be a number. Example: 321')
args = parser.parse_args()


def main(resource, series, dip_file, project_name, folder_end):
    """Main function, which is run when this script is executed"""
    am_client = AMClient(
        ss_api_key=config.get("Archivematica", "api_key"), 
        ss_user_name=config.get("Archivematica", "username"), 
        ss_url=config.get("Archivematica", "ss_baseurl"))
    aspace = ASpace()
    aspace_token = aspace.client.authorize()
    print("Starting...")
    dip_data = get_candidate_dips(am_client, project_name, folder_end)
    for component_uri in get_candidate_uris(aspace, resource, series):
        try:
            dip = match_component_to_dip(aspace, component_uri, dip_data)
            dip_uuid, title, aip_uuid = get_dip_info(dip)
            dao_uri = post_dao(aspace_token, dip_uuid, title, aip_uuid)
            update_component(aspace, component_uri, dao_uri)
        except Exception as e:
            print(e)


def get_candidate_dips(am_client, project_name, folder_end):
    '''Gets all DIPs from the Archivematica Storage Service and returns DIPs that match specific criteria.

    Args:
        am_client (am_client.AMClient.am_client): instantiation of am_client
        project_name (str): collection or other name expected to be part of SIP name
        folder_end (int): assumes "Folder" is in DIP name, folder # to stop at

    Returns:
        list of Archivematica DIPs (array)
    '''
    all_dips = am_client.dips()
    candidate_dips = []
    for dip in all_dips:
        original_name = dip['current_path'][40:-37]
        if project_name in original_name and folder_end > original_name.split('Folder')[1]:
            candidate_dips.append(dip)
    return candidate_dips


def get_candidate_uris(aspace, resource_id, series_id):
    """Takes a resource and a series from that resource to return all file-level
    descendants of the series that do not have linked digital objects.

    Args:
        aspace (asnake.aspace.ASpace): instantiation of ASpace
        resource_id (str): ArchivesSpace ID of resource. Example: 123
        series_id (str): ArchivesSpace ID of series. Example: 4321

    Returns:
        list of ArchivesSpace URIs (array)
    """

    series_tree = aspace.client.get(
        'repositories/2/resources/{}/tree/node?node_uri=/repositories/2/archival_objects/{}'.format(
            resource_id, series_id)).json()
    uri_list = []
    for subseries in series_tree.get("children"):
        for file_level in subseries.get("children"):
            if "digital_object" not in file_level.get("instance_types"):
                uri_list.append(file_level['record_uri'])
    return uri_list


def match_component_to_dip(aspace, ao_uri, dip_list):
    """Using box and folder indicators, matches an ArchivesSpace component to a DIP.

    Args:
        aspace (asnake.aspace.ASpace): instantiation of ASpace
        ao_uri (str): ArchivesSpace URI of an archival object
        dip_list (array): List of dictionaries of DIP information

    Returns:
        DIP information (dictionary)
    """
    ao = aspace.client.get(
        ao_uri, params={"resolve": ["top_container"]}).json()
    box = ao.get('instances')[0].get('sub_container').get(
        'top_container').get('_resolved')['indicator']
    folder = ao.get('instances')[0].get('sub_container').get('indicator_2')
    dip = [dip for dip in dip_list if (
        dip.get("folder") == folder and dip.get("box") == box)]
    if len(dip) == 1:
        dip = dip[0]
        return dip
    else:
        raise Exception(
            "Error for {}: {} matches found, expected 1.".format(
                ao_uri, len(dip)))


def get_dip_info(dip):
    """Parses DIP information to return DIP UUID, title to be used as DAO title, and UUID of associated AIP.

    Args:
        dip (dictionary): DIP information

    Returns:
        UUID, file title, and associated AIP UUID (tuple)
    """
    dip_uuid = dip['uuid']
    title = dip['current_full_path'].split('/')[-1][:-37]
    aip_uuid = dip['related_packages'][0].split('/')[-2]
    return dip_uuid, title, aip_uuid


def post_dao(aspace, dip_uuid, title, aip_uuid):
    """Creates a digital object in ArchivesSpace

    Args:
        aspace (asnake.aspace.ASpace): instantiation of ASpace
        dip_uuid (str): DIP UUID
        title (str): DAO title
        aip_uuid (str): AIP UUID

    Returns:
        DAO URI (string)
    """
    file_uri = join("http://storage.rockarch.org/",
                    "{}-{}.pdf".format(dip_uuid, title))
    data = {"jsonmodel_type": "digital_object",
            "is_slug_auto": True,
            "file_versions": [{"jsonmodel_type": "file_version",
                               "is_representative": False,
                               "file_uri": str(file_uri),
                               "xlink_actuate_attribute": "onRequest",
                               "xlink_show_attribute": "new",
                               "file_format_name": "pdf",
                               "file_format_version": "Generic PDF",
                               "publish": True}],
            "restrictions": False,
            "notes": [{"jsonmodel_type": "note_digital_object",
                       "content": [str(aip_uuid)],
                       "type": "originalsloc",
                       "publish": False}],
            "title": str(title),
            "digital_object_id": str(dip_uuid)}
    r = aspace.post("repositories/2/digital_objects", json=data)
    if r.status_code != 200:
        raise Exception("Could not post {}: {}".format(
            title, r.json().get('error')))
    else:
        return r.json().get("uri")


def update_component(aspace, component, dao):
    """Add a digital object to an archival object

    Args:
        aspace (asnake.aspace.ASpace): instantiation of ASpace
        component (str): ArchivesSpace URI for archival object
        dao (str): ArchivesSpace URI for digital object

    Returns:
        Response from ArchivesSpace
    """
    updated_component = aspace.client.get(component).json()
    updated_component["instances"].append(
        {
            "instance_type": "digital_object",
            "jsonmodel_type": "instance",
            "digital_object": {
                "ref": dao}})
    r = aspace.client.post(component, json=updated_component)
    if r.status_code != 200:
        raise Exception("Could not post {} to {}: {}".format(
            dao, component, r.json().get('error')))


if __name__ == "__main__":
    main(args.resource, args.series, args.dip_info_file, args.project_name, args.folder_end)
