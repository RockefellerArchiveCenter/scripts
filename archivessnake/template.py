#!/usr/bin/env python3

"""A template for ArchivesSnake scripts.

Contains default arguments for AS username and password, as well as the AS
baseurl (optional, defaults to development instance).

Creates an instance of ASpace using the credentials and baseurl passed.
"""

import argparse

from asnake import utils
from asnake.aspace import ASpace


def main(resource_id):
    aspace = ASpace()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='A template for ArchivesSnake scripts.')
    args = parser.parse_args()
    main(*args)
