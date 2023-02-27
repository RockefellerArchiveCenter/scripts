#!/usr/bin/env python

import os
import json
import time
from asnake.aspace import ASpace
from asnake.utils import get_note_text

def note_content_identical(notes, aspace):
    content = []
    for note in notes:
        content.append(" ".join(get_note_text(note, aspace.client)))
    return len(set(content)) < len(notes)

def get_ao_notes(aspace):
    for object in repo.archival_objects:
        unpublish_notes(object, aspace)

def unpublish_notes(object, aspace):
    object_json = object.json()
    has_duplicate_notes = False
    processing_notes = [n for n in object_json.get("notes") if n.get("type") == "processinfo"]
    if len(processing_notes):
        if note_content_identical(processing_notes, aspace):
            has_duplicate_notes = True
    if has_duplicate_notes:
        print(object.uri, object.ref_id, object.resource.id_0)

if __name__ == '__main__':
    aspace = ASpace()
    repo = aspace.repositories(2)
    start_time = time.time()
    get_ao_notes(aspace)
    elapsed_time = time.time() - start_time
    print('Time Elapsed: ' + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
