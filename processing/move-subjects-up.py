#!/usr/bin/env python3

import argparse

from asnake.aspace import ASpace
from asnake.utils import walk_tree


def main(resource_id):
    client = ASpace().client

    # Skip the first item in the iterable since it is the resource itself
    tree = walk_tree(f'/repositories/2/resources/{resource_id}', client)
    next(tree)

    for obj in tree:
        if obj['level'] in ['file', 'item'] and len(obj['subjects']):
            parent = client.get(obj["parent"]["ref"]).json()
            if parent['level'] not in ['file', 'item']:
                combined_subjects = parent['subjects'] + obj['subjects']
                parent['subjects'] = [dict(t) for t in {tuple(d.items()) for d in combined_subjects}]
                client.post(parent['uri'], json=parent)
                obj['subjects'] = []
                client.post(obj['uri'], json=obj)
                print(f'Subjects removed from {obj["uri"]} and assigned to {parent["uri"]}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Moves subjects assigned at the file level up to the next level.')
    parser.add_argument(
        'resource_id',
        help='The ArchivesSpace ID for a resource record')
    args = parser.parse_args()
    main(args.resource_id)
