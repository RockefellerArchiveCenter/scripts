#!/usr/bin/env python3

import argparse

from asnake.aspace import ASpace
from asnake.utils import walk_tree


def main(resource_id, baseurl, username, password):
    client = ASpace(
          baseurl=baseurl,
          username=username,
          password=password).client

    resource = client.get(f'/repositories/2/resources/{resource_id}').json()

    # Skip the first item in the iterable since it is the resource itself
    tree = walk_tree(f'/repositories/2/resources/{resource_id}', client)
    next(tree)

    for obj in tree:
        if obj['level'] not in ['file', 'item']:
            deduped_subjects = [s for s in resource['subjects'] if s not in obj['subjects']]
            print("Resource subjects", resource["subjects"])
            print("object subjects", obj["subjects"])
            print(deduped_subjects)
            print("\n")
            resource['subjects'] = deduped_subjects

    client.post(f'/repositories/2/resources/{resource_id}', json=resource)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Remove subjects from resources when they are assigned at lower levels in the same collection.')
    parser.add_argument(
        'resource_id',
        help='The ArchivesSpace ID for a resource record')
    parser.add_argument(
        'username',
        help='An ArchivesSpace user with write permissions')
    parser.add_argument(
        'password',
        help='The password for the ArchivesSpace user')
    parser.add_argument(
        '--baseurl',
        help='The base URL for an ArchivesSpace instance',
        default='https://as.dev.rockarch.org/api')
    args = parser.parse_args()
    main(args.resource_id, args.baseurl, args.username, args.password)
