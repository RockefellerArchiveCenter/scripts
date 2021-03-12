#!/usr/bin/env python3

import argparse
from configparser import ConfigParser

from asnake.aspace import ASpace

config = ConfigParser()
config.read("local_settings.cfg")

def process_tree(client, resource):
    """Iterates through a given collection, file, or series provided by user input.
    Finds note content that matches user input and then deletes or modifies
    relevant notes according to user preference.  """
    for record in resource.tree.walk:
        aojson = record.json()
        if aojson["title"].startswith("Foundation-Administered Project (FAP)"):
            aojson["title"] = handle_fap_title(aojson["title"])
        notes = aojson.get("notes")
        for note in notes:
            for subnote in note.get("subnotes", []):
                subnote_content = add_semicolon_spaces(subnote.get("content", ""))
                if subnote_content.isupper():
                    subnote_content = to_sentence_case(subnote_content)
                subnote["content"] = subnote_content
        save_record(record.uri, client, aojson)
        print("updated", aojson["uri"])


def to_sentence_case(text):
    """Converts an uppercase string to sentence case."""
    return ". ".join(t.capitalize() for t in text.split(". "))


def add_semicolon_spaces(text):
    """Adds spaces after semicolons in text."""
    return "; ".join([t.strip() for t in text.split(";")]).strip()


def handle_fap_title(title):
    split = title.split(": ")
    for idx, text in enumerate(split):
        split[idx] = text.title() if text.isupper() else text
    return ": ".join(split)


def save_record(uri, client, data):
    """Posts modifications/deletions to ArchivesSpace"""
    updated = client.post(uri, json=data)
    try:
        updated.raise_for_status()
    except Exception as e:
        raise Exception(updated.json()) from e


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("resource_id", type=int, help="The identifier of the resource record in which you want to search. Found in the URL.")
    return parser


def main():
    """Main function, which is run when this script is executed"""
    parser = get_parser()
    args = parser.parse_args()
    aspace = ASpace(
        baseurl=config.get("ArchivesSpace", "baseurl"),
        username=config.get("ArchivesSpace", "username"),
        password=config.get("ArchivesSpace", "password"))
    process_tree(
        aspace.client,
        aspace.repositories(config.get("ArchivesSpace", "repository")).resources(args.resource_id))


if __name__ == "__main__":
    main()
