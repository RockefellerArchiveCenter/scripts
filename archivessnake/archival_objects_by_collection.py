#!/usr/bin/env python

"""Exports information about all archival objects in a resource tree.

   usage: python archival_objects_by_collection.py resource_id
"""

import argparse
import csv
import json
import os

from asnake.aspace import ASpace

OUTPUT_FILE = "data.csv"

class DataFetcher:
    def __init__(self, resource_id):
        if os.path.isfile(OUTPUT_FILE):
            raise Exception(F"{OUTPUT_FILE} already exists and would be overwritten. Please move or delete this file before running the script again.")
        self.aspace = ASpace()
        self.repo = self.aspace.repositories(2)
        self.resource_id = int(resource_id)

    def run(self):
        writer = csv.writer(open(OUTPUT_FILE, 'w'))
        for record in self.repo.resources(self.resource_id).tree.walk:
            if record.jsonmodel_type == 'archival_object':
                data = self.get_object_data(record)
                print(data)
                writer.writerow(data)

    def get_object_data(self, obj):
        return [obj.uri, obj.resource.title, obj.ancestors[0].title, self.get_title(obj),
                self.get_dates(obj.dates), self.get_instances(obj.instances),
                self.get_folders(obj.instances), self.get_notes(obj.notes),
                self.get_location(obj.instances)]

    def get_title(self, data):
        try:
            return data.title
        except:
            return data.display_string

    def get_dates(self, dates_array):
        dates = []
        for date in dates_array:
            try:
                dates.append(date.expression)
            except KeyError:
                try:
                    dates.append("{}-{}".format(date.begin, date.end))
                except KeyError:
                    dates.append(date.end)
        return ", ".join(dates)

    def get_instances(self, instances_array):
        instances = []
        for instance in instances_array:
            top_container = self.aspace.client.get(instance.sub_container.top_container.ref).json()
            instances.append(top_container['display_string'])
        return ", ".join(instances)

    def get_folders(self, instances_array):
        folders = []
        for instance in instances_array:
            folders.append("{} {}".format(instance.sub_container.type_2, instance.sub_container.indicator_2))
        return ", ".join(folders)

    def get_notes(self, notes_array):
        notes = []
        for note in notes_array:
            if note.type not in ['accessrestrict', 'userestrict']:
                if note.jsonmodel_type == 'note_singlepart':
                    notes.append("{}: {}".format(note.type, " ".join([c for c in note.content])))
                else:
                    notes.append("{}: {}".format(note.type, " ".join([c.content for c in note.subnotes])))
        return ', '.join(notes)

    def get_location(self, instances_array):
        locations = []
        for instance in instances_array:
            top_container = self.aspace.client.get(instance.sub_container.top_container.ref).json()
            for loc in top_container['container_locations']:
                l = self.aspace.client.get(loc['ref']).json()
                locations.append(l['title'])
        return ", ".join(locations)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetches data about all archival objects associated with a collection.')
    parser.add_argument('resource_id', help='Identifier for a resource record')
    args = parser.parse_args()
    DataFetcher(args.resource_id).run()
