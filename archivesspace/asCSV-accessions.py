#!/usr/bin/env python

import os
import requests
import json
import logging
import ConfigParser
import csv
import time
from datetime import datetime
from codecs import encode, decode

config = ConfigParser.ConfigParser()
config.read('local_settings.cfg')

# Logging configuration
logging.basicConfig(
    filename=config.get('Logging', 'filename'),
    format=config.get('Logging', 'format', 1),
    datefmt=config.get('Logging', 'datefmt', 1),
    level=config.get('Logging', 'level', 0))

# Sets logging of requests to WARNING to avoid unneccessary info
logging.getLogger("requests").setLevel(logging.WARNING)

dictionary = {
    'baseURL': config.get('ArchivesSpace', 'baseURL'),
    'repository': config.get('ArchivesSpace', 'repository'),
    'user': config.get('ArchivesSpace', 'user'),
    'password': config.get('ArchivesSpace', 'password')}

repositoryBaseURL = '{baseURL}/repositories/{repository}'.format(**dictionary)
resourceURL = '{baseURL}'.format(**dictionary)

# authenticates the session
auth = requests.post('{baseURL}/users/{user}/login?password={password}&expiring=false'.format(**dictionary)).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session}

# creates the spreadsheet
writer = csv.writer(open('accessions.csv', 'w'))


def get_extent_data(object):
    data = {}
    if 'extents' in object:
        for extent in object['extents']:
            if extent['portion'] == 'whole':
                container_summary = extent.get('container_summary', None)
                data = dict(
                    [('container_summary', container_summary),
                     ('extent_number', extent['number']),
                     ('extent_type', extent['extent_type'])])
    return data


def get_delivery_date(object):
    date = ''
    if 'user_defined' in object:
        if 'date_1' in object['user_defined']:
            date = object['user_defined']['date_1']
    return date


def get_number(object):
    number = object['id_0']
    if 'id_1' in object:
        number = '{}.{}'.format(number, object['id_1'])
        if 'id_2' in object:
            number = '{}.{}'.format(number, object['id_2'])
    return number


def make_row(accession):
    row = []
    extent_data = get_extent_data(accession)
    delivery_date = get_delivery_date(accession)
    accession_date = accession.get('accession_date', None)
    acquisition_type = accession.get('acquisition_type', None)
    container_summary = extent_data.get('container_summary', None)
    extent_number = extent_data.get('extent_number', None)
    extent_type = extent_data.get('extent_type', None)
    row.append(accession_date)
    row.append(accession['title'].encode('utf-8'))
    row.append(get_number(accession))
    row.append(container_summary)
    row.append(extent_number)
    row.append(extent_type)
    row.append(acquisition_type)
    row.append(delivery_date)
    writer.writerow(row)


def main():
    created_before = datetime.now()
    created_after = start_date_entry = datetime(1974, 01, 01, 0, 0)
    start_date_entry = raw_input('Enter a start date in YYYY-MM-DD format (hit enter for no start date): ')
    end_date_entry = raw_input('Enter an end date in YYYY-MM-DD format (hit enter to export everything after the start date): ')
    if len(end_date_entry):
        created_before = datetime.strptime(str(end_date_entry), "%Y-%m-%d")
    if len(start_date_entry):
        created_after = datetime.strptime(str(start_date_entry), "%Y-%m-%d")

    column_headings = ['accession date', 'title', 'number', 'container summary',
                       'extent number', 'extent type', 'acquisition type', 'delivery date']
    writer.writerow(column_headings)

    accessionIds = requests.get(
        '{}/accessions'.format(repositoryBaseURL), headers=headers,
        params={"all_ids": True}).json()

    if 'error' in accessionIds:
        print accessionIds['error']
        return False

    for accessionId in reversed(accessionIds):
        accession = (requests.get('{}/accessions/{}'.format(repositoryBaseURL, str(accessionId)), headers=headers)).json()
        accession_created = datetime.strptime(accession['create_time'], '%Y-%m-%dT%H:%M:%SZ')
        if (accession_created > created_after) and (accession_created < created_before):
            print 'Writing accession', str(accessionId)
            make_row(accession)


main()
