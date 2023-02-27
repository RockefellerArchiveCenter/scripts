#!/usr/bin/env python

"""
Deletes top containers not associated with any collections.

usage: python delete_orphan_containers.py
"""

import json
from datetime import date

from asnake.aspace import ASpace


class ContainerDeleter:
    def __init__(self):
        self.aspace = ASpace()
        self.repo = self.aspace.repositories(2)

    def run(self):
        delete_count = 0
        for container in self.repo.search.with_params(q="types:top_container AND empty_u_sbool:true", all_ids=True):
            deleted = self.aspace.client.delete(container.uri)
            print(container.uri)
            delete_count += 1
        with open('deleted.txt', 'a') as out_file:
            today = str(date.today())
            out_file.write("Deleted {} top containers on {}.\n".format(delete_count, today))

if __name__ == "__main__":
    ContainerDeleter().run()
