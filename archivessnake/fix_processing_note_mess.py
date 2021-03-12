#!/usr/bin/env python

"""
Removes duplicate Processing Information notes and repopulates missing note
text from EAD
"""

import argparse
import csv
from pathlib import Path

from asnake.aspace import ASpace
from configparser import ConfigParser
import xml.etree.ElementTree as ET

config = ConfigParser()
config.read("local_settings.cfg")

aspace = ASpace(
              baseurl=config.get("ArchivesSpace", "baseURL"),
              username=config.get("ArchivesSpace", "user"),
              password=config.get("ArchivesSpace", "password"),
    )

ns = {'ead': 'urn:isbn:1-931666-22-9'}
ead_directory = Path(__file__).absolute().parent.parent.parent.joinpath("data", "ead") # assumes that EAD directory is a sibling of scripts directory

def main(csv_path):
    with open(csv_path, "r", encoding='utf-8-sig') as df:
        csv_reader = csv.reader(df)
        for uri, ref_id, ead_id in csv_reader:
            if not(all([uri, ref_id, ead_id])):
                exit()
            try:
                tree = ET.parse(ead_directory.joinpath(ead_id, "{}.xml".format(ead_id)))
                root = tree.getroot()
                ead_notes = root.findall(".//*ead:c[@id='{}']/*".format(ref_id), ns)
                resp = aspace.client.get(uri)
                resp.raise_for_status()
                as_object = resp.json()
                delete_duplicate(as_object)
                append_replaced(as_object, ead_notes)
                updated = aspace.client.post(uri, json=as_object)
                if updated.status_code == 200:
                    print("{} updated".format(uri))
                else:
                    print("{} error".format(uri))
                    pass
            except FileNotFoundError:
                print("Cannot find {}".format(ead_directory.joinpath(ead_id, "{}.xml".format(ead_id))))
                pass

def delete_duplicate(object):
    """Removes notes with duplicate persistent_id values."""

    note_ids = []
    for idx, note in enumerate(reversed(object.get("notes", []))):
        if note["persistent_id"] in note_ids:
            del object["notes"][-(idx+1)]
            break
        else:
            note_ids.append(note["persistent_id"])

def append_replaced(object, ead_notes):
    """Adds notes present in EAD but not in AS JSON."""

    note_ids = [n["persistent_id"] for n in object.get("notes", [])]
    for note in ead_notes:
        raw_tag = note.tag.replace(ns["ead"], "").replace("{}", "")
        if raw_tag not in ["did", "c", "controlaccess", "head", "thead"]:
            if note.attrib["id"] not in note_ids:
                note_content = "\n\n".join(s.text for s in note.findall("ead:p", ns))
                new_note = {
                    "jsonmodel_type": "note_multipart",
                    "persistent_id": note.attrib["id"],
                    "type": raw_tag,
                    "subnotes": [
                        {
                            "jsonmodel_type": "note_text",
                            "content": note_content,
                            "publish": True
                        }
                    ],
                    "publish": True
                }
                object["notes"].append(new_note)

parser = argparse.ArgumentParser(description="Removes duplicate processinfo notes and adds missing content")
parser.add_argument('csv_path', help='Path to a CSV file containing URIs and ref_ids')
args = parser.parse_args()

main(args.csv_path)
