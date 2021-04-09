#!/usr/bin/env python3

"""Clears the image cache for a range of images, and clears the info cache.

Usage: clear_cache.py identifier start_page end_page username secret

Clears the image cache for a range of images, and clears the info cache.

positional arguments:
  identifier  Base identifier for the image
  start_page  First page to clear cache
  end_page    Last page to clear cache
  username    Authorized user for the Cantaloupe API
  secret      Secret for the authorized user
"""

import argparse
import requests
import json


class CacheClearer(object):

    def clear_cache(self, identifier, start_page, end_page, username, secret):
        for x in range(int(end_page) - int(start_page) + 1):
            current_page = str(int(start_page) + x).zfill(3)
            current_image = "{}_{}".format(identifier, current_page)
            payload = {
                "verb" : "PurgeItemFromCache",
                "identifier" : current_image
            }
            resp = requests.post("https://images.rockarch.org/tasks", json=payload, auth=(username, secret))
            resp.raise_for_status()
            print("Cleared cached for {}".format(current_image))
        resp = requests.post("https://images.rockarch.org/tasks", json={"verb" : "PurgeInfoCache"}, auth=(username, secret))
        resp.raise_for_status()
        print("Info cache cleared")



parser = argparse.ArgumentParser(description="Clears the image cache for a range of images, and clears the info cache.")
parser.add_argument('identifier', help='Base identifier for the image')
parser.add_argument('start_page', help='First page to clear cache')
parser.add_argument('end_page', help='Last page to clear cache')
parser.add_argument('username', help='Authorized user for the Cantaloupe API')
parser.add_argument('secret', help='Secret for the authorized user')
args = parser.parse_args()

CacheClearer().clear_cache(args.identifier, args.start_page, args.end_page, args.username, args.secret)
