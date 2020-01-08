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
        self.get_title()
        self.get_id()
        for obj in self.get_objects():
            print(obj.title)
            if self.has_instance(obj):
                self.get_container(container)
                self.get_parent(obj)
                print('hello')

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

    def has_instance(self, obj):
        """
        Checks whether the object has a container instance and returns the top container link.
        """
        if len(obj.instances) > 0:
            for instance in obj.instances:
                if 'sub_container' in instance.json():
                    container = instance.sub_container.top_container.ref
                    container = container[31:]
                    return container
        else:
            return False

    def get_container(self, container):
        """
        Gets and returns top container information.
        """
        type = self.repo.top_containers(container).type
        indicator = self.repo.top_containers(container).indicator

    def get_parent(self, obj):
        """
        Checks whether the object has a parent and returns it
        """
        if obj.parent:
            parent = obj.parent.ref
            parent = parent[33:]
            parentTitle = self.repo.archival_objects(parent).title
            print(parentTitle)
            return parentTitle
        else:
            pass



parser = argparse.ArgumentParser(description="Creates a csv with container labels based on a a given resource ID.")
parser.add_argument('-r', '--resource', help='Target a specific resource')
args = parser.parse_args()

LabelPrinter(args.resource).run()
