#!/usr/bin/env python

import argparse
import configparser
import json

from asnake.aspace import ASpace

class LabelPrinter:
    def __init__(self, resource):
        config = configparser.ConfigParser()
        config.read('local_settings.cfg')
        self.aspace = ASpace(baseurl=config.get('ArchivesSpace', 'baseURL'), username=config.get('ArchivesSpace', 'user'), password=config.get('ArchivesSpace', 'password'))
        self.repo = self.aspace.repositories(2)
        self.resource = resource

    def run(self):
        for obj in self.get_objects():
            resourceTitle = self.get_title()
            resourceId = self.get_id()
            parent = self.get_parent(obj)
            container = self.get_container(obj)
            print(resourceTitle, resourceId, parent, container)

    def get_objects(self):
        """
        Fetches and returns all the archival objects from that resource tree.
        """
        objects = self.repo.resources(self.resource).tree.walk
        return objects

    def get_title(self):
        """
        Gets and returns the title of a resource record.
        """
        title = self.repo.resources(self.resource).title
        return title

    def get_id(self):
        """
        Gets and returns the id of a resource record.
        """
        id = self.repo.resources(self.resource).id_0
        return id

    def get_container(self, obj):
        """
        Checks whether the object has a container instance and returns the top container link.
        """
        containers = []
        for instance in obj.instances:
            try:
                top_container = instance.sub_container.top_container
                containers.append("{} {} ".format(top_container.type.capitalize(), top_container.indicator))
            except AttributeError as e:
                pass
        return ", ".join(containers)

    def get_parent(self, obj):
        """
        Checks whether the object has a parent and returns it
        """
        try:
            return obj.parent.title
        except AttributeError:
            return ''


parser = argparse.ArgumentParser(description="Creates a csv with container labels based on a a given resource ID.")
parser.add_argument('-r', '--resource', help='Target a specific resource')
args = parser.parse_args()

LabelPrinter(args.resource).run()
