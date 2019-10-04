#!/usr/bin/env python

"""
Adds dates to components using ArchivesSpace's date calculator endpoint.

usage: python add_missing_dates.py --levels --undated_only --resource
"""

import argparse
import configparser
import json
import os

from asnake.aspace import ASpace


LEVELS = ["class", "collection", "fonds", "otherlevel", "recordgrp", "series",
          "subfonds", "subgrp", "subseries"]


class DateCalculator:
    def __init__(self, levels, always_add=False, resource=None):
        config = configparser.ConfigParser()
        config.read('local_settings.cfg')
        self.aspace = ASpace(baseurl=config.get('ArchivesSpace', 'baseURL'), username=config.get('ArchivesSpace', 'username'), password=config.get('ArchivesSpace', 'password'))
        self.repo = self.aspace.repositories(2)
        self.levels = levels if levels else LEVELS
        self.always_add = always_add
        self.resource = resource

    def run(self):
        """Main method for this class, which processes a list of objects."""
        for obj in self.get_objects():
            if (obj.level in self.levels) and (self.is_undated(obj)):
                date = self.calculate_date(obj.uri)
                if date:
                    obj_json = obj.json()
                    if self.always_add:
                        obj_json['dates'] = [date]
                    else:
                        obj_json['dates'].append(date)
                    self.save_obj(obj_json)

    def get_objects(self):
        """
        If a resource is passed, fetches all the archival objects from that
        resource tree, otherwise returns all archival objects.
        """
        objects = self.repo.resources(self.resource).tree.walk if self.resource else self.repo.archival_objects
        return objects

    def is_undated(self, obj):
        """
        Returns True unless there is a date object with a date expression that
        doesn't match common patterns for undated materials.
        """
        if not self.always_add:
            if len(obj.dates) > 0:
                for date in obj.dates:
                    if date.expression not in ['undated', 'Undated', 'unknown', 'nd', 'n.d.']:
                        return False
        return True

    def calculate_date(self, uri):
        """Calls the date calculator endpoint and returns a date object."""
        calculated = self.aspace.client.get('/date_calculator', params={'record_uri': uri}).json()
        expression = "{}-{}".format(calculated['min_begin'], calculated['max_end'])
        date = {'expression': expression, 'begin': calculated['min_begin_date'],
                'end': calculated['max_end_date'], 'date_type': 'inclusive',
                'label': 'creation'} if (calculated['min_begin'] and calculated['max_end']) else None
        return date

    def save_obj(self, obj_json):
        """Saves an updated object to ArchivesSpace"""
        updated = self.aspace.client.post(obj_json['uri'], json=obj_json)
        if updated.status_code == 200:
            print("Dates updated for {}".format(obj_json['uri']))
        else:
            print(updated.json())

parser = argparse.ArgumentParser(description="Adds dates to components using ArchivesSpace's date calculator endpoint.")
parser.add_argument('-l', '--levels', action='append', choices=LEVELS, help='Archival object levels to include in date calculation.')
parser.add_argument('-a', '--always_add', action='store_true', help='Always add dates, even if component has existing dates.')
parser.add_argument('-r', '--resource', help='Restrict replace to a specific resource')
args = parser.parse_args()

DateCalculator(args.levels, args.always_add, args.resource).run()
