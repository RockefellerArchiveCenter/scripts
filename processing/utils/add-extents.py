#!/usr/bin/env python3

import argparse

from asnake.aspace import ASpace
from asnake.utils import walk_tree


def main(resource_id):
    client = ASpace().client

    for obj in walk_tree(f'/repositories/2/resources/{resource_id}', client):
        if obj["level"] not in ["file", "item"]:
            extent = client.get('extent_calculator', params={'record_uri': obj["uri"], 'units': 'feet'}).json()
            if extent["total_extent"] > 0:
                obj["extents"] = [{
                    'number': str(extent["total_extent"]),
                    'portion': 'whole',
                    'extent_type': 'Cubic Feet',
                    'container_summary': f'{extent["container_count"]} {"container" if extent["container_count"] == 1 else "containers"}',
                    'jsonmodel_type': 'extent'}]
            updated = client.post(obj["uri"], json=obj)
            if updated.status_code == 200:
                print(f"Updated extent on {obj['uri']}")
            else:
                print(updated.json())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Add extent statements to non file-level components in a resource record.')
    parser.add_argument(
        'resource_id',
        help='The ArchivesSpace ID for a resource record')
    args = parser.parse_args()
    main(args.resource_id)
