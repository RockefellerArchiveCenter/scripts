#!/usr/bin/env python

"""Splits a file containing a JSON array into individual files for each item.

usage: split_json.py [-h] filepath

Args:
    filepath (str): File path of JSON file to split into separate files.
"""

import argparse
import json
import os


class JSONSplitter:
    def __init__(self, filepath, key):
        self.filepath = filepath
        self.key = key
        with open(filepath, 'r') as jf:
            self.data = json.load(jf)

    def split(self):
        for obj in self.data:
            with open(os.path.join(os.path.split(self.filepath)[0], f"{obj[self.key]}.json", 'w+') as df:
                json.dump(obj, df, indent=2)
        os.remove(self.filepath)

parser = argparse.ArgumentParser(description='Splits JSON arrays into individual files.')
parser.add_argument('filepath', help='File path of JSON file to split into separate files.')
parser.add_argument('key', help='Key in the individual JSON objects to use as a filename.')
args = parser.parse_args()

JSONSplitter(args.filepath, args.key).split()
