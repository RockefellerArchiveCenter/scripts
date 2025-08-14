#!/usr/bin/env python3

from os import getenv
from pathlib import Path
from shutil import rmtree

import shortuuid
from asnake.aspace import ASpace
from requests import Session

"""Removes locally-stored packages that have been ingested and are available on DIMES.

Iterates over a parent directory containing subdirectories which are named using
AS refids. If the DIMES object corresponding to that refid has a digital object,
the subdirectory is deleted.

Requires the following environment variables:
- AS_BASEURL
- AS_USERNAME
- AS_PASSWORD
- AS_REPO_ID
- PARENT_DIR (parent directory in which packages are located.)
"""

class DigitalObjectRemover(object):

    def __init__(self):
        self.dimes_client = Session()
        self.dimes_client.headers.update({'Accept': 'application/json'})
        self.as_client = ASpace(
            baseurl=getenv('AS_BASEURL'),
            username=getenv('AS_USERNAME'),
            password=getenv('AS_PASSWORD')
        ).client

    def remove_dirs(self):
        for fp in Path(getenv('PARENT_DIR')).iterdir():
            if fp.is_dir() and len(fp.stem) == 32:
                try:
                    uri = self.dimes_url_from_refid(fp.stem)
                    self.check_object(uri)
                    print(f"Removing {str(fp)}")
                    rmtree(fp)
                except Exception as e:
                    print(fp.stem, e)

    def dimes_url_from_refid(self, refid):
        resp = self.as_client.get(f"/repositories/{getenv('AS_REPO_ID')}/find_by_id/archival_objects?ref_id[]={refid}")
        resp.raise_for_status()
        results = resp.json()
        if len(results.get("archival_objects")) == 1:
            as_uri = results['archival_objects'][0]['ref']
            return f"/objects/{shortuuid.uuid(as_uri)}"
        else:
            raise Exception(f"{results.get('archival_objects')} results found for ref_id {refid}.")

    def check_object(self, url):
        resp = self.dimes_client.get(f"https://api.rockarch.org{url}")
        resp.raise_for_status()
        object_data = resp.json()
                        
        assert object_data['online'], f'online attribute for {url} is false'
        
        object_id = url.split("/")[-1]
        pdf_url = f"https://iiif.rockarch.org/pdfs/{object_id}"
        resp = self.dimes_client.head(pdf_url)
        assert resp.status_code == 200, f'PDF is not available for {url}'
        
        manifest_url = f"https://iiif.rockarch.org/manifests/{object_id}"
        resp = self.dimes_client.head(manifest_url)
        assert resp.status_code == 200, f'IIIF Manifest is not available for {url}'

if __name__ == '__main__':
    DigitalObjectRemover().remove_dirs()