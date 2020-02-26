#!/usr/bin/env python3

"""
Walks a resource tree and replaces date expressions which fall into bad and
predictable patterns. Also includes a flag to "touch" archival objects, in
order to trigger Timewalk.

usage: python add_missing_dates.py resource -t
"""

import argparse
import configparser
import json
import os

from asnake.aspace import ASpace


CIRCA_VARIANTS = ["Circa", "circa.", "ca.", "C.A.", "c.", "C.",
                  "approximately", "About", "about", "probably", "possibly"]
UNDATED_VARIANTS = ["No date", "No Date", "no date", "n/d", "N/D", "N. D.",
                    "n. d.", "n/a", "N/A", "n.d", "n.d.",
                    "Date Not Yet Determined", "date?", "Date?", "unknown",
                    "Unknown", "unkown", "undated ms.", "Early undated",
                    "Year?", "Various Dates"]
MONTH_MATCHES = [("Jan.", "January"), ("Feb.", "February"), ("Mar.", "March"),
                 ("Apr.", "April"), ("Jun.", "June"), ("Jul.", "July"),
                 ("Aug.", "August"), ("Sep.", "September"),
                 ("Oct.", "October"), ("Nov.", "November")]
REMOVE_STRINGS = ["Exhibited: ", "d. "]


class ExpressionReplacer:
    def __init__(self, resource, touch=False):
        config = configparser.ConfigParser()
        config.read('local_settings.cfg')
        self.aspace = ASpace(baseurl=config.get('ArchivesSpace', 'baseURL'),
                             username=config.get('ArchivesSpace', 'username'),
                             password=config.get('ArchivesSpace', 'password'))
        self.repo = self.aspace.repositories(2)
        self.resource = resource
        self.touch = touch

    def run(self):
        """Main method for this class, which processes a list of objects."""
        for obj in self.repo.resources(self.resource).tree.walk:
            self.updated = False
            obj_json = obj.json()
            for date in obj_json.get("dates"):
                self.replace_circa(date)
                self.replace_undated(date)
                self.replace_months(date)
                self.remove_strings(date)
            if (self.touch or self.updated):
                self.save_obj(obj_json)

    def replace_circa(self, date):
        for variant in CIRCA_VARIANTS:
            if date["expression"].startswith(variant):
                date["expression"] = date["expression"].replace(variant, "circa")
                self.updated = True

    def replace_undated(self, date):
        for variant in UNDATED_VARIANTS:
            if date["expression"].strip() == variant:
                date["expression"] = date["expression"].replace(variant, "undated")
                self.updated = True

    def replace_months(self, date):
        for abbreviation, full_month in MONTH_MATCHES:
            if date["expression"].startswith(abbreviation):
                date["expression"] = date["expression"].replace(abbreviation, full_month)
                self.updated = True

    def remove_strings(self, date):
        for remove in REMOVE_STRINGS:
            if date["expression"].startswith(remove):
                date["expression"] = date["expression"].replace(remove, "")
                self.updated = True

    def save_obj(self, obj_json):
        """Saves an updated object to ArchivesSpace"""
        updated = self.aspace.client.post(obj_json['uri'], json=obj_json)
        if updated.status_code == 200:
            print("Archival object {} updated".format(obj_json['uri']))
        else:
            print(updated.json())


parser = argparse.ArgumentParser(description="Replaces problematic strings in date expressions and optionally updates the last saved time of all archival objects in a resource tree.")
parser.add_argument('resource', help='ID of the resource whose tree should be processed.')
parser.add_argument('-t', '--touch', action='store_true', help='Trigger a save on each archival object.')
args = parser.parse_args()

ExpressionReplacer(args.resource, args.touch).run()
