#!/usr/bin/env python3

"""Get data about all top containers without RAC-standard barcodes."""

import csv

from asnake import utils
from asnake.aspace import ASpace


def main():
    aspace = ASpace()
    with open("bs_barcodes.csv", "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['uri', 'barcode', 'indicator', 'series', 'resource_title', 'resource_id'])
        for top_container in aspace.repositories(2).top_containers:
            barcode = getattr(top_container, 'barcode', None)
            series_title = top_container.series[0].display_string if len(top_container.series) else None
            resource_title = top_container.collection[0].title if len(top_container.collection) else None
            resource_id = utils.format_resource_id(top_container.collection[0], aspace.client) if len(top_container.collection) else None
            if not barcode or not barcode.startswith("A000"):
                writer.writerow([
                    top_container.uri,
                    barcode, 
                    top_container.indicator,
                    series_title,
                    resource_title,
                    resource_id,])


if __name__ == '__main__':
    main()
