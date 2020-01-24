#!/usr/bin/env python3

import csv
import configparser
import json
import requests
import time

from asnake.client import ASnakeClient
import asnake.logging as logging
from asnake.aspace import ASpace
from configparser import ConfigParser, ExtendedInterpolation

logging.setup_logging(filename='logging.txt', level='INFO', filemode='a')
logger = logging.get_logger()

config = configparser.ConfigParser()
config.read('local_settings.cfg')

aspace = ASpace(baseurl=config['ArchivesSpace']['baseURL'],
                user=config['ArchivesSpace']['user'],
                password=config['ArchivesSpace']['password'])
repo = aspace.repositories(config['ArchivesSpace']['repository'])


def get_collection():
    """Returns a collection corresponding to an ID provided by user input"""
    try:
        identifier = input('Resource ID: ')
        return repo.resources(int(identifier))
    except Exception as e:
        raise Exception("Unable to get collection: {}".format(e))


def has_local_name(agent):
    """Loops through all the agent names and returns True if any of them have
    a source of `local`, `ingest`, `nad`, or `naf`"""
    for name in agent.names:
        if name.source in ['local', 'ingest', 'nad', 'naf']:
            return True
    return False


def remove_local_agents(collection):
    """Removes all locally-authorized agents from a collection"""
    for ao in collection.tree.walk:
        updated = False
        data = ao.json()
        for i, agent in reversed(list(enumerate(ao.linked_agents))):
            if has_local_name(agent):
                data['linked_agents'].pop(i)
                updated = True
                logger.info("{} will be deleted from {}".format(agent.uri, ao.uri))
                print("{} will be deleted from {}".format(agent.uri, ao.uri))
        if updated:
            updated_ao = aspace.client.post(ao.uri, json=data)
            logger.info("{} updated".format(ao.uri))
            print("{} updated".format(ao.uri))


def main():
    """Main function, which is run when this script is executed"""
    start_time = time.time()
    collection = get_collection()

    try:
        print("Preparing to delete agents from {}...".format(collection.uri))
        remove_local_agents(collection)
        elapsed_time = time.time() - start_time
        print("Time Elapsed: " + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
    except Exception as e:
        print(e)


main()
