#!/usr/bin/env python3

"""Remove whitespace and lowercase a from barcodes."""

import csv

from asnake import utils
from asnake.aspace import ASpace


URI_LIST = ['/repositories/2/top_containers/12617']

def main():
    client = ASpace().client
    for uri in URI_LIST:
        top_container = client.get(uri).json()
        normalized = top_container['barcode'].strip()
        if normalized.startswith('a'):
            normalized = normalized.replace('a', 'A', 1)
        top_container['barcode'] = normalized
        resp = client.post(uri, json=top_container)
        if resp.status_code != 200:
            print(resp.json())
        else:
            print(uri)
        

if __name__ == '__main__':
    main()
