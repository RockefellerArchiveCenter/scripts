#!/usr/bin/env python3

import argparse
from requests import Session


class DigitalObjectChecker(object):

    def __init__(self):
        self.client = Session()
        self.client.headers.update({'Accept': 'application/json'})
        self.processed = 0
        self.unprocessed = 0

    def check_children(self, parent_uri):
        children = self.get_children(parent_uri)
        self.process_children(children)
        return self.processed, self.unprocessed

    def get_children(self, parent_uri):
        resp = self.client.get(f"https://api.rockarch.org/{parent_uri.lstrip('/').rstrip('/')}/children?limit=200").json()
        children = resp['results']
        while resp['next']:
            resp = self.client.get(resp['next']).json()
            children += resp['results']
        return children

    def process_children(self, children):
        for child in children:
            if child['type'] == 'collection':
                children = self.get_children(child['uri'])
                self.process_children(children)
            else:
                full_data = self.client.get(f"https://api.rockarch.org{child['uri']}").json()
                self.check_object(full_data)

    def check_object(self, object_data):
        try:
            object_id = object_data['uri'].split("/")[-1]
            assert object_data['online'], 'online attribute is false'
            
            pdf_url = f"https://iiif.rockarch.org/pdfs/{object_id}"
            resp = self.client.head(pdf_url)
            assert resp.status_code == 200, 'PDF is not available'
            
            manifest_url = f"https://iiif.rockarch.org/manifests/{object_id}"
            resp = self.client.head(manifest_url)
            assert resp.status_code == 200, 'IIIF Manifest is not available'
            self.processed += 1
        except AssertionError as e:
            as_uri = [i['identifier'] for i in object_data['external_identifiers'] if i['source'] == 'archivesspace'][0]
            print(object_data['uri'], object_data['title'], as_uri, e)
            self.unprocessed += 1

def main(parent_uri):
    processed, unprocessed = DigitalObjectChecker().check_children(parent_uri)
    print(f"\n{processed} processed, {unprocessed} unprocessed")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check digital assets for all objects associated with a parent collection.')
    parser.add_argument('parent_uri', help='DIMES URI of parent.')
    args = parser.parse_args()
    main(args.parent_uri)