#!/usr/bin/env python

"""
Splits instances and assigns containers to each instance based on container indicator.

usage: python split_instances.py separator resource containers_list
"""

import argparse
import json

from asnake.aspace import ASpace


class InstanceSplitter:
    def __init__(self, separator, resource, containers_list):
        self.aspace = ASpace()
        self.repo = self.aspace.repositories(2)
        self.separator = separator
        self.resource = resource
        self.containers_list = containers_list

    def run(self):
        with open(self.containers_list, 'r') as cl:
            containers = json.load(cl)
            for obj in self.repo.resources(self.resource).tree.walk:
                if len(obj.instances):
                    data = obj.json()
                    reel_numbers = self.get_reel_numbers(obj.instances)
                    for i, n in enumerate(reel_numbers):
                        try:
                            data['instances'][i]['sub_container']['top_container']['ref'] = containers["R{}".format(n.lstrip("R-"))]
                        except KeyError:
                            print("Could not find top container matching indicator {} for object {}".format("R{}".format(n.lstrip("R-")), obj.uri))
                            continue
                        except IndexError:
                            data['instances'].append(
                                {"instance_type": data['instances'][0]['instance_type'],
                                 "jsonmodel_type": "instance",
                                 "sub_container": {
                                    "jsonmodel_type": "sub_container",
                                    "top_container": {"ref": containers["R{}".format(n.lstrip("R-"))]}
                                    }})
                    updated = self.aspace.client.post(obj.uri, json=data).json()
                    try:
                        print(updated['uri'])
                    except KeyError:
                        print(updated)

    def get_reel_numbers(self, instances):
        reel_numbers = []
        for instance in instances:
            if instance.instance_type == 'microform':
                top_container = self.aspace.client.get(instance.sub_container.top_container.ref).json()
                for r in top_container.get('indicator').split(self.separator):
                    reel_numbers.append(r)
        return reel_numbers

parser = argparse.ArgumentParser(description="Splits instances in a resource record based on a separator.")
parser.add_argument('separator', help='Separator character which divides instances')
parser.add_argument('resource', help='ArchivesSpace ID of resource record to target')
parser.add_argument('containers_list', help='List of dicts where indicator number is the key and container URI is the value')
args = parser.parse_args()

InstanceSplitter(args.separator, args.resource, args.containers_list).run()
