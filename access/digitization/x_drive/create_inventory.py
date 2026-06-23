#!/usr/bin/env python3

import argparse
import csv
from datetime import datetime
from pathlib import Path

import shortuuid
from asnake.aspace import ASpace
from asnake.utils import get_date_display, find_closest_value
from dateutil import parser, relativedelta
from requests.sessions import Session

INVENTORY_FILENAME = f"inventory_{int(datetime.now().timestamp())}.csv"
AS_REPO = 2
AEON_BASEURL = "https://raccess.rockarch.org/aeonapi"
API_BASEURL = "https://api.rockarch.org/"
FIELDNAMES = ["current_path", "uri", "refid", "title", "start_date", "end_date", "resource_title", "resource_date", "already_online", "dimes_id"]


class AeonClient(object):
    """Client to connect to Aeon"""

    def __init__(self, baseurl, access_key):
        self.session = Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'AeonClient/0.1',
            'X-AEON-API-KEY': access_key
        })
        self.baseurl = baseurl

    def get(self, url):
        """Handles HTTP GET requests."""
        full_url = "/".join([self.baseurl.rstrip("/"), url.lstrip("/")])
        return self.session.get(full_url)
    

class RacApiClient(object):
    def __init__(self, baseurl):
        self.session = Session()
        self.session.headers.update({'Accept': 'application/json'})
        self.baseurl = baseurl

    def get_object(self, obj_id):
        full_url = "/".join([self.baseurl.rstrip("/"), "objects", obj_id])
        return self.session.get(full_url).json()


def main(base_dir, aeon_access_key):
    """Main method which calls all other submethods."""
    aeon_client = AeonClient(AEON_BASEURL, aeon_access_key)
    as_client = ASpace().client
    rac_api_client = RacApiClient(API_BASEURL)

    output_path = Path(".", INVENTORY_FILENAME)
    with open(output_path, "w") as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=FIELDNAMES)
        csv_writer.writeheader()
        for fp in Path(base_dir).iterdir():
            if is_processable(fp):
                current_filepath = str(fp)
                transaction_number = fp.stem
                refid = None
                try:
                    refid = get_aeon_data(aeon_client, transaction_number)
                    if not refid:
                        raise Exception(f"No refid found for transaction {transaction_number}")
                    uri, title, start_date, end_date, resource_title, resource_date = get_as_data(as_client, refid)
                    dimes_id, already_online = get_online_status(uri, rac_api_client)
                    csv_writer.writerow({
                        "current_path": current_filepath, 
                        "uri": uri, 
                        "refid": refid, 
                        "title": title, 
                        "start_date": start_date, 
                        "end_date": end_date,
                        "resource_title": resource_title, 
                        "resource_date": resource_date,
                        "already_online": already_online,
                        "dimes_id": dimes_id})
                except Exception as e:
                    print(transaction_number, refid, e)


def is_processable(file_path):
    """Determines if file path represents a valid Aeon transaction.
    
    Args:
        file_path (pathlib.Path): file path to evaluate.

    Returns:
        is_processible (bool): whether file path is processable
    """
    return bool(file_path.is_dir() and len(file_path.stem) == 6 and file_path.stem.isdigit())

        
def get_aeon_data(client, transaction_number):
    """Fetches data about a transaction from Aeon.
    
    Args:
        client (AeonClient): instance of Aeon client
        transaction_number (str): Aeon transaction number

    Returns:
        (str): ref ID from Aeon transaction, which is saved in itemCitation field
    """
    resp = client.get(f"/Requests/{transaction_number}")
    resp.raise_for_status()
    return resp.json()['itemCitation']

def format_aspace_date(start_date, end_date):
        """Formats ASpace dates so that they can be parsed by Aquila.
        Assumes beginning of month or year if a start date, and end of month or
        year if an end date.

        Args:
            start_date (str): unformatted start date
            end_date (str): unformatted end date

        Returns:
            formatted_start_date (str): start date in format YYYY-MM-DD
            formatted_start_date (str): end date in format YYYY-MM-DD
        """
        parsed_start = parser.isoparse(start_date)
        parsed_end = parser.isoparse(end_date)
        formatted_start = parsed_start.strftime('%Y-%m-%d')
        if len(end_date) == 4:
            formatted_end = (
                parsed_end + relativedelta.relativedelta(
                    month=12, day=31)).strftime('%Y-%m-%d')
        elif len(end_date) == 7:
            formatted_end = (
                parsed_end + relativedelta.relativedelta(
                    day=31)).strftime('%Y-%m-%d')
        else:
            formatted_end = end_date
        return formatted_start, formatted_end

def get_as_dates(client, obj):
    dates = find_closest_value(obj, 'dates', client)
    try:
        if dates[0]['date_type'] == 'single':
            return format_aspace_date(dates[0]['begin'], dates[0]['begin'])
        else:
            start_date = sorted([d['begin'] for d in dates])[0] # earliest start date
            end_date = sorted([d['end'] for d in dates])[-1] # latest end date
            return format_aspace_date(start_date, end_date)
    except Exception as e:
        print(e)
        return "", ""

def get_as_data(client, refid):
    """Fetches data about an archival object from ArchivesSpace.
    
    Args:
        client (asnake.ASpace.client): instance of ArchivesSpace client
        refid (str): ref ID for archival object

    Returns:
        uri, title, start_date, end_date, resource_title, resource_date (tuple): data from ArchivesSpace
    """
    resp = client.get(f'/repositories/{AS_REPO}/find_by_id/archival_objects?ref_id[]={refid}&resolve[]=archival_objects::resource').json()
    if not len(resp["archival_objects"]) == 1:
        raise Exception(f"{len(resp['archival_objects'])} results found for refid {refid}")
    obj = resp['archival_objects'][0]['_resolved']
    resource = obj['resource']['_resolved']
    uri = obj['uri']
    title = obj.get('title', obj['display_string'])
    start_date, end_date = get_as_dates(client, obj)
    resource_title = resource['title']
    resource_date = ", ".join([get_date_display(n, client) for n in resource['dates']])
    return uri, title, start_date, end_date, resource_title, resource_date

def get_online_status(as_uri, client):
    dimes_id = shortuuid.uuid(name=as_uri)
    obj = client.get_object(dimes_id)
    return dimes_id, obj['online']

if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Creates inventory of in-house digitized content for rights assessment.')
    p.add_argument('base_dir', help='The base directory to iterate through.')
    p.add_argument('aeon_access_key', help='Secret access key for Aeon API.')
    args = p.parse_args()
    main(args.base_dir, args.aeon_access_key)