#!/usr/bin/env python

import argparse
import json
import os


class JSONSplitter:
    def __init__(self, filepath):
        self.filepath = filepath
        with open(filepath, 'r') as jf:
            self.data = json.load(jf)

    def split(self):
        for obj in self.data:
            with open(os.path.join(os.path.split(self.filepath)[0], "{}.json".format(obj['id'])), 'w+') as df:
                json.dump(obj, df, indent=2)
        os.remove(self.filepath)

parser = argparse.ArgumentParser(description='Splits JSON arrays into individual files.')
parser.add_argument('filepath', help='File path of JSON file to split into separate files.')
args = parser.parse_args()

JSONSplitter(args.filepath).split()
