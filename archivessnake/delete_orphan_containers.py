#!/usr/bin/env python

"""
Deletes top containers not associated with any collections.

usage: python delete_orphan_containers.py
"""

import configparser
import json

from asnake.aspace import ASpace


class ContainerDeleter:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('local_settings.cfg')
        self.aspace = ASpace(baseurl=config.get('ArchivesSpace', 'baseURL'), username=config.get('ArchivesSpace', 'username'), password=config.get('ArchivesSpace', 'password'))
        self.repo = self.aspace.repositories(config.get('ArchivesSpace', 'repository'))

    def run(self):
        for container in self.repo.search.with_params(q="types:top_container AND empty_u_sbool:true", all_ids=True):
            deleted = self.aspace.client.delete(container.uri)
            print(container.uri)
            with open('deleted.txt', 'w') as out_file:
                out_file.write(json.dumps(out))

ContainerDeleter().run()
