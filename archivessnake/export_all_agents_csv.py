#!/usr/bin/env python

import os
import json
import csv
from asnake.aspace import ASpace


aspace = ASpace()
repo = aspace.repositories(2)

###Writes agent data to a csv
def write_agent_csv(csvName):
    fieldnames = ['URI', 'agent']
    with open(csvName, 'w', newline='') as outputFile:
        writer = csv.DictWriter(outputFile, fieldnames=fieldnames)
        writer.writeheader()
        get_agents(writer)

###Gets agents
def get_agents(writer):
    for object_type in ['agents']:
        for object in getattr(aspace, object_type):
            if object.used_within_repositories == ['/repositories/2']:
                print("agents/{}".format(object.uri.split('/')[-1]))
                writer.writerow({'URI': str(object.uri), 'agent': object.title})

csvName = "agents.csv"
write_agent_csv(csvName)
