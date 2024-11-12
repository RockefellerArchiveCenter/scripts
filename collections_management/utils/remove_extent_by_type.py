#!/usr/bin/env python3

# usage: remove_extent_by_type.py extent_type

# Removes extents matching a specific extent type from archival objects.

# positional arguments:
#   extent_type  Extent type to remove.

import argparse

from asnake.aspace import ASpace


def main(extent_type):
    client = ASpace().client
    for obj in client.get_paged(f'repositories/{client.config["repo_id"]}/search?q=extents:{extent_type}&type[]=archival_object&fields[]=uri'):
        archival_object = client.get(obj['uri']).json()
        extents = archival_object['extents']
        changed = False
        for idx, e in enumerate(reversed(extents)):
            if e['extent_type'] == extent_type:
                extents.pop(idx)
                changed = True
        if changed:
            archival_object['extents'] = extents
            client.post(archival_object['uri'], json=archival_object)   
            print(f"Extents with type {extent_type} removed from archival_object['uri']")             

if __name__ =='__main__':
    parser = argparse.ArgumentParser(description="Removes extents matching a specific extent type from archival objects.")
    parser.add_argument('extent_type', type=str, help='Extent type to remove.')
    args = parser.parse_args()
    main(args.extent_type)