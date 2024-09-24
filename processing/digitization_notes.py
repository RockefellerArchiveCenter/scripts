#!/usr/bin/env python

"""
Based on a CSV-formatted digitization manifest, adds or deletes Conditions Governing
Access notes to objects slated for outsourced digitization.
"""

import argparse
import json
from csv import DictReader
from asnake.aspace import ASpace
from asnake.utils import get_note_text


NOTE_STRING = "Restricted - Temporarily unavailable."

def main(csv_filepath, operation):
    client = ASpace().client
    with open(csv_filepath, 'r') as csv_file:
        reader = DictReader(csv_file)
        for row in reader:
            refid = row.get('filename', row['file_name_root'])
            obj_data = get_object_by_refid(client, refid)
            matching_notes = [note for note in obj_data['notes'] if get_note_text(note, client) == [NOTE_STRING]]
            if operation == 'add':
                if len(matching_notes) == 0:
                    obj_data['notes'].append(
                        {
                            "jsonmodel_type": "note_multipart",
                            "label": "Conditions Governing Access note",
                            "publish": True,
                            "subnotes": [
                                {
                                    "content": NOTE_STRING,
                                    "jsonmodel_type": "note_text",
                                    "publish": True
                                }
                            ],
                            "type": "accessrestrict"
                        }                    
                    )
                    resp = client.post(obj_data['uri'], json.dumps(obj_data))
                    resp.raise_for_status()
                    print(f"Digitization note added to {refid}")
            elif operation == 'delete':
                if len(matching_notes) >= 1:
                    updated_notes = [note for note in obj_data['notes'] if get_note_text(note, client) != [NOTE_STRING]]
                    obj_data['notes'] = updated_notes
                    resp = client.post(obj_data['uri'], json.dumps(obj_data))
                    resp.raise_for_status()
                    print(f"Digitization note removed from {refid}")

def get_object_by_refid(client, refid):
    results = client.get(f"/repositories/2/find_by_id/archival_objects?ref_id[]={refid}").json()
    if len(results.get("archival_objects")) == 1:
        as_uri = results['archival_objects'][0]['ref']
        return client.get(as_uri).json()
    else:
        raise Exception(f"{results.get('archival_objects')} results found for ref_id {refid}.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add or remove Conditions Governing Access to objects in outsourced digitization processes.')
    parser.add_argument('csv_filepath', help='File path to digitization manifest (CSV format).')
    parser.add_argument('operation', help='The action (add or delete) to take.', choices=['add', 'delete'])
    args = parser.parse_args()
    main(args.csv_filepath, args.operation)