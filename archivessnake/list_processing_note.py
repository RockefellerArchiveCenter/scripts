#!/usr/bin/env python

import os
import json
import time
from asnake.aspace import ASpace
from asnake.utils import get_note_text

aspace = ASpace()
repo = aspace.repositories(2)

repo = aspace.repositories(2)
start_time = time.time()


def note_content_identical(notes):
    content = []
    for note in notes:
        content.append(" ".join(get_note_text(note, aspace.client)))
    return len(set(content)) < len(notes)

def get_resources_notes():
    for object in aspace.resources:
        if object.id_0.startswith('FA') and object.publish:
            unpublish_notes(object)

def get_ao_notes():
    for object in repo.archival_objects:
        unpublish_notes(object)

def unpublish_notes(object):
    object_json = object.json()
    has_duplicate_notes = False
    processing_notes = [n for n in object_json.get("notes") if n.get("type") == "processinfo"]
    if len(processing_notes):
        if note_content_identical(processing_notes):
            has_duplicate_notes = True
    if has_duplicate_notes:
        print(object.uri, object.ref_id, object.resource.id_0)

# get_resources_notes()

get_ao_notes()

elapsed_time = time.time() - start_time
print('Time Elapsed: ' + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
