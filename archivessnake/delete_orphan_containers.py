#!/usr/bin/env python

"""
Deletes top containers not associated with any collections.

usage: python delete_orphan_containers.py
"""

import configparser
import json

from asnake.aspace import ASpace
from datetime import date


class ContainerDeleter:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('local_settings.cfg')
        self.aspace = ASpace(baseurl=config.get('ArchivesSpace', 'baseURL'), username=config.get('ArchivesSpace', 'username'), password=config.get('ArchivesSpace', 'password'))
        self.repo = self.aspace.repositories(config.get('ArchivesSpace', 'repository'))

    def run(self):
        n = 0
        for container in self.repo.search.with_params(q="types:top_container AND empty_u_sbool:true", all_ids=True):
            deleted = self.aspace.client.delete(container.uri)
            print(container.uri)
            n += 1
        with open('deleted.txt', 'a') as out_file:
            today = str(date.today())
            out_file.write("Deleted {} top containers on {}.\n".format(n, today))

ContainerDeleter().run()
