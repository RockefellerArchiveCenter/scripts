#!/usr/bin/env python

import os, requests, json, logging, ConfigParser, csv
from codecs import encode
from codecs import decode

config = ConfigParser.ConfigParser()
config.read('local_settings.cfg')

# Logging configuration
logging.basicConfig(filename=config.get('Logging', 'filename'),format=config.get('Logging', 'format', 1), datefmt=config.get('Logging', 'datefmt', 1), level=config.get('Logging', 'level', 0))
# Sets logging of requests to WARNING to avoid unneccessary info
logging.getLogger("requests").setLevel(logging.WARNING)

dictionary = {'baseURL': config.get('ArchivesSpace', 'baseURL'), 'repository':config.get('ArchivesSpace', 'repository'), 'user': config.get('ArchivesSpace', 'user'), 'password': config.get('ArchivesSpace', 'password')}
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
    for extent in object['extents']:
        if extent['portion'] == 'whole':
            container_summary = extent['container_summary'] if 'container_summary' in extent else ''
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
        number = number + '.' + object['id_1']
        if 'id_2' in object:
            number = number + '.' + object['id_2']
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
    column_headings = ['accession date', 'title', 'number', 'container summary',
                       'extent number', 'extent type', 'acquisition type', 'delivery date']
    writer.writerow(column_headings)
    accessionIds = requests.get(repositoryBaseURL + '/accessions?all_ids=true', headers=headers).json()
    for accessionId in reversed(accessionIds):
        accession = (requests.get(repositoryBaseURL + '/accessions/' + str(accessionId), headers=headers)).json()
        print 'Writing accession', str(accessionId)
        make_row(accession)

main()
