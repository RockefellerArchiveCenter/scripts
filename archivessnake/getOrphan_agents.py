#!/usr/bin/env python

import os
import json
import csv
from asnake.aspace import ASpace


def write_agent_csv(csvName, aspace):
    """Writes orphan agent data to a csv"""
    fieldnames = ['URI', 'agent']
    with open(csvName, 'w', newline='') as outputFile:
        writer = csv.DictWriter(outputFile, fieldnames=fieldnames)
        writer.writeheader()
        get_agents(writer, aspace)

def get_agents(writer, aspace):
    """Gets orphan agents"""
    for object_type in ['agents']:
        for object in getattr(aspace, object_type):
            if object.used_within_repositories == []:
                aspace.get().json()
                #print(object)
                print("agents/{}".format(object.uri.split('/')[-1]))
                writer.writerow({'URI': str(object.uri), 'agent': object.title})

if __name__ == "__main__":
    aspace = ASpace()
    csvName = "orphan_agents.csv"
    write_agent_csv(csvName, aspace)
