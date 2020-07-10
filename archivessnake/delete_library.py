
#!/usr/bin/env python

import os
import json
from asnake.aspace import ASpace
import configparser

config = ConfigParser()
config.read("local_settings.cfg")
aspace = ASpace(
              baseurl=config.get("ArchivesSpace", "baseURL"),
              username=config.get("ArchivesSpace", "user"),
              password=config.get("ArchivesSpace", "password"),
    )
repo = aspace.repositories(2)

#Expects a CSV file with column resource_id, subject_id, agent_person_id, agent_corporate_entity_id or agent_family_id to be deleted from AS

def delete_resources(data):
    with open(data, newline='') as data:
        reader = csv.DictReader(data)
        for row in reader:
            try:
                uri = "/repositories/2/resources/"
                resource_id = str(row['resource_id'])
                delete = aspace.client.delete(uri + resource_id)
                print("deleted resource "+ resource_id)
            except:
                pass

def delete_subjects(data):
    with open(data, newline='') as data:
        reader = csv.DictReader(data)
        for row in reader:
            try:
                uri = "/subjects/"
                subject_id = str(row['subject_id'])
                delete = aspace.client.delete(uri + subject_id)
                print("deleted subject "+ subject_id)
            except:
                pass


def delete_agents_person(data):
    with open(data, newline='') as data:
        reader = csv.DictReader(data)
        for row in reader:
            try:
                uri = "/agents/people/"
                agent_person_id = str(row['agent_person_id'])
                delete = aspace.client.delete(uri + agent_person_id)
                print("deleted "+ agent_person_id)
            except:
                pass

def delete_agents_corporate_entities(data):
    with open(data, newline='') as data:
        reader = csv.DictReader(data)
        for row in reader:
            try:
                uri = "/agents/corporate_entities/"
                agent_corporate_entity_id = str(row['agent_corporate_entity_id'])
                delete = aspace.client.delete(uri + agent_corporate_entity_id)
                print("deleted agent_corporate_entity "+ agent_corporate_entity_id)
            except:
                pass

def delete_agents_families(data):
    with open(data, newline='') as data:
        reader = csv.DictReader(data)
        for row in reader:
            try:
                uri = "/agents/families/"
                agent_family_id = str(row['agent_family_id'])
                delete = aspace.client.delete(uri + agent_family_id)
                print("deleted agent_family "+ agent_family_id)
            except:
                pass

def delete_top_containers(data):
    with open(data, newline='') as data:
        reader = csv.DictReader(data)
        for row in reader:
            try:
                uri = '/repositories/2/top_containers/'
                top_container_id = str(row['top_container_id'])
                delete = aspace.client.delete(uri + top_container_id)
                print("deleted top_container " + top_container_id)
            except:
                pass
data = "top_container.csv"

#delete_resources(data)
#delete_subjects(data)
#delete_agents_corporate_entities(data)
#delete_agents_families(data)
delete_top_containers(data)
