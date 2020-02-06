#!/usr/bin/env python

import argparse
import json
import os


class DataModifier:
    def __init__(self, filepath):
        self.filepath = filepath

    def add_ids(self):
        for f in os.listdir(self.filepath):
            with open(os.path.join(self.filepath, f), 'r') as jf:
                data = json.load(jf)
                idx = data.get('index')
                for ex_id in data.get('external_identifiers'):
                    identifier = int(ex_id.get('identifier').split('/')[-1])
                    if idx != identifier:
                        print("NO MATCH", f)


parser = argparse.ArgumentParser(description='Adds identifiers to URIs based on indexes.')
parser.add_argument('filepath', help='File path of directory containing JSON files to update.')
args = parser.parse_args()

DataModifier(args.filepath).add_ids()
