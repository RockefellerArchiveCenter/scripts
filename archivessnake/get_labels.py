#!/usr/bin/env python

import argparse
import configparser
import json
import csv
import os.path

from asnake.aspace import ASpace


class LabelPrinter:
    def __init__(self, resource):
        config = configparser.ConfigParser()
        config.read("local_settings.cfg")
        self.aspace = ASpace(
            baseurl=config.get("ArchivesSpace", "baseURL"),
            username=config.get("ArchivesSpace", "user"),
            password=config.get("ArchivesSpace", "password"),
        )
        self.resource = self.aspace.repositories(2).resources(resource)

    def run(self):
        label_data = []
        resource_title = self.resource.title
        resource_id = self.get_id()
        for obj in self.resource.tree.walk:
            if len(obj.instances):
                parent = self.get_parent(obj)
                container = self.get_containers(obj)
                print(resource_title, resource_id, parent, container)
                label_data.append([resource_title, resource_id, parent, container])
        self.make_csv(set(tuple(row) for row in label_data))

    def make_csv(self, label_data):
        with open("box_labels.csv", "w") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["ResourceTitle", "ResourceID", "ParentTitle", "Container"])
            writer.writerows(label_data)

    def get_id(self):
        """
        Gets and returns the id of a resource record.
        """
        number = []
        for n in range(0, 3):
            try:
                number.append(getattr(self.resource, "id_{}".format(n)))
            except AttributeError:
                break
        return ":".join(number)

    def get_containers(self, obj):
        """
        Iterates throught the instances in an object and returns the container type and indicator.
        """
        containers = []
        for instance in obj.instances:
            try:
                top_container = instance.sub_container.top_container
                containers.append(
                    "{} {}".format(
                        top_container.type.capitalize(), top_container.indicator
                    )
                )
            except KeyError as e:
                pass
        return ", ".join(containers)

    def get_parent(self, obj):
        """
        Checks whether the object has a parent and returns it
        """
        try:
            return obj.parent.title
        except AttributeError:
            return ""


parser = argparse.ArgumentParser(
    description="Creates a csv with container labels based on a a given resource ID."
)
parser.add_argument("resource", help="ArchivesSpace resource id")
args = parser.parse_args()

LabelPrinter(args.resource).run()
