#!/usr/bin/env python3

"""A template for ArchivesSnake scripts.

Contains default arguments for AS username and password, as well as the AS
baseurl (optional, defaults to development instance).

Creates an instance of ASpace using the credentials and baseurl passed.
"""

import argparse

from asnake import utils
from asnake.aspace import ASpace


def main(resource_id, baseurl, username, password):
    aspace = ASpace(
          baseurl=baseurl,
          username=username,
          password=password)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='A template for ArchivesSnake scripts.')
    parser.add_argument(
        'username',
        help='An ArchivesSpace user with write permissions')
    parser.add_argument(
        'password',
        help='The password for the ArchivesSpace user')
    parser.add_argument(
        '--baseurl',
        help='The base URL for an ArchivesSpace instance',
        default='https://as.dev.rockarch.org/api')
    args = parser.parse_args()
    main(args.baseurl, args.username, args.password)
