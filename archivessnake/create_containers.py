#!/usr/bin/env python

"""
Creates top containers given an Excel spreadsheet containing indicators and barcodes.

usage: python create_containers.py spreadsheet
"""

import argparse
import json
import openpyxl

from asnake.aspace import ASpace


class ContainerCreator:
    def __init__(self, spreadsheet):
        self.aspace = ASpace()
        self.repo_id = 2
        self.container_data = openpyxl.load_workbook(spreadsheet).active

    def run(self):
        """
        Creates top containers and returns the URI. Or, if a top container with
        a matching barcode already exists, returns its URI instead.
        """
        out = {}
        for row in self.container_data.iter_rows():
            indicator = "R{}".format(row[2].value.lstrip("Reel ").lstrip("R"))
            barcode = row[9].value if row[9].value else None
            container_data = {"indicator": indicator,
                              "type": "reel",
                              "barcode": barcode,
                              "container_profile": {"ref": row[10].value}}
            new_container = self.aspace.client.post("repositories/{}/top_containers".format(self.repo_id), json=container_data).json()
            if new_container.get('error'):
                print(new_container['error'])
                new_container = self.get_existing_container(barcode).json()
            print({indicator: new_container.get('uri')})
            out[indicator] = new_container.get('uri')
            with open('created.txt', 'w') as out_file:
                out_file.write(json.dumps(out))
        print(out)

    def get_existing_container(self, barcode):
        results = self.aspace.repositories(self.repo_id).search.with_params(q='primary_type:top_container AND barcode_u_sstr:{}'.format(barcode))
        for result in results:
            return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Creates containers given a spreadsheet with indicator and barcode information.")
    parser.add_argument('spreadsheet', help='Filepath to Excel spreadsheet')
    args = parser.parse_args()
    ContainerCreator(args.spreadsheet).run()
