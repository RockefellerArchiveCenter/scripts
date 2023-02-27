#!/usr/bin/env python

# Creates or updates a digitization manifest.

# positional arguments:
#   output_filename  File path for the manifest.
#   {av,text}        The format of the materials to be digitized.

# options:
#   -h, --help       show this help message and exit
#   --ref_id REF_ID  ArchivesSpace RefID of an archival object to add to the
#                    manifest.
#   --series SERIES  ArchivesSpace RefID of a series containing archival objects
#                    to add to the manifest.
#   --file FILE      File containing a list of comma-separated ArchivesSpace
#                    RefIDs of objects to add to the manifest.

from csv import DictWriter
from argparse import ArgumentParser
from os.path import splitext
from pathlib import Path

from asnake.aspace import ASpace
from asnake.utils import get_note_text, walk_tree

REPO_ID = 2

TEXT_FIELDNAMES = {
            "box_number": "Box", 
            "folder_number": "Folder", 
            "title": "Title", 
            "filename": "Filename"
        }

AV_FIELDNAMES = {
            'shipping_date': 'Shipping Date',
            'shipping_box_number': 'Shipping Box Number',
            'rac_box_number': 'RAC Box Number',
            'object_unique_identifier': 'Object Unique Identifier(s)',
            'number_of_units': 'Number of Original Media Units',
            'program_unique_identifier': 'Program Unique Identifier',
            'original_format': 'Original Format',
            'original_recording_date': 'Original Recording Date/Interview Date',
            'title': 'Title (of recording)',
            'series': 'Series',
            'file_name_root': 'File Name Root',
            'notes_to_engineer_speed': 'Notes to Engineer: Speed (based on annotations)',
            'notes_to_engineer': 'Notes to Engineer',
            'format_specific_notes_tape': 'Format-Specific Notes - Tape Standard',
            'format_specific_notes': 'Format-Specific Notes - Brand',
            'audio_reel_size': 'Audio Reel Size',
        }


def object_data(ref_id, client):
    """Fetches data about an archival object from ArchivesSpace.

    Args:
        ref_id (str): RefID for an archival object
        client (asnake.aspace.ASpace instance): ASpace client

    Returns:
        archival_object_data (dict): JSON data about the archival object
    """
    results = client.get(f"/repositories/{REPO_ID}/find_by_id/archival_objects?ref_id[]={ref_id}&resolve[]=archival_objects").json()
    if len(results['archival_objects']) != 1:
        raise Exception(f'Expecting to get only on result for ref id {ref_id} but got {len(results["archival_objects"])} instead.')
    return results['archival_objects'][0]['_resolved']    

def series_data(ref_id, client):
    """Fetches data about archival objects contained within a series.
    
    Args:
        ref_id (str): RefID for an archival object
        client (asnake.aspace.ASpace instance): ASpace client

    Returns:
        series_data (generator): List of dictionaries with data about archival objects in the series.
    """
    parent = object_data(ref_id, client)
    tree = walk_tree(parent["uri"], client)
    next(tree) # skip first item, which is the parent.
    return tree

def parse_input_file(filepath):
    """Parses a list of values from a file.
    
    Args:
        filepath (str): Location of input file to parse.

    Returns:
        text (list): list of values.
    """
    with open(filepath, 'r') as input_file:
        text = input_file.read()
    return [refid.strip() for refid in text.split(',')]

def format_output_filename(filename):
    """Returns a normalized filename for the output file.
    
    Args:
        filename (str): Filename passed into the function by the user.

    Returns:
        normalized (str): Normalized output filename.
    """
    basename = splitext(filename)[0]
    return f"{basename.replace(' ', '_')}.csv"

def get_av_number(instances):
    """Returns AV number for an archival object.
    
    Args:
        instances (list): ArchivesSpace instance data.

    Returns:
        av_number (str): AV number for the archival object.
    """
    av_numbers = [instance.get('sub_container', {}).get('indicator_2') for instance in instances if instance.get('sub_container', {}).get('indicator_2').startswith('AV')]
    return ', '.join(number for number in av_numbers if number is not None)

def get_box_number(top_containers):
    """Parses box numbers from instances.
    
    Args:
        top_containers (list): ArchivesSpace top_container data.

    Returns:
        box_number (str): A comma-separated string of box numbers.
    """
    return ', '.join([container['indicator'] for container in top_containers])

def get_folder_number(instances):
    """Parses folder numbers from instances.
    
    Args:
        instances (list): ArchivesSpace instance data.

    Returns:
        folder_number (str): A comma-separated string of folder numbers.
    """
    folder_numbers = [instance.get('sub_container', {}).get('indicator_2') for instance in instances]
    return ', '.join([number for number in folder_numbers if number is not None])

def get_format(notes, client):
    """Parses the format of the original item from ArchivesSpace archival object data.
    
    Args:
        notes (list): ArchivesSpace notes data.

    Returns:
        format (str): Format of the archival object.
    """
    materialspec = [note for note in notes if note['type'] == 'materialspec']
    if len(materialspec):
        return ", ".join(get_note_text(materialspec[0], client))
    return None

def get_date(dates):
    """Parses dates from ArchivesSpace archival object.
    
    Args:
        dates (dict): ArchivesSpace dates data.

    Returns:
        dates (str): comma-separated list of dates in ISO-8601 format.
    """
    formatted = []
    for date in dates:
        if date['date_type'] == 'single':
            formatted.append(date['begin'])
        else:
            formatted.append(f"{date['begin']} - {date['end']}")
    return ', '.join(formatted)

def get_parent(top_containers):
    """Parses series name from ArchivesSpace archival object.
    
    Args:
        top_containers (dict): ArchivesSpace top_container data.

    Returns:
        series (str): Title of the object's parent.
    """
    return ', '.join([container['series'][0]['display_string'] for container in top_containers])

def get_title(data):
    """Returns a title for an archival object.
    
    Args:
        data (dict): ArchivesSpace archival object data.

    Returns:
        title (str): Title of the archival object.
    """
    try:
        return data['title']
    except KeyError:
        return data['display_string']

def format_data(unformatted_objects, format, client):
    for obj in unformatted_objects:
        top_containers = [
            client.get(instance['sub_container']['top_container']['ref']).json() for
            instance in obj['instances'] if 'sub_container' in instance
        ]
        if format == 'av':
            yield {
                'shipping_date': '',
                'shipping_box_number': '',
                'rac_box_number': get_box_number(top_containers),
                'object_unique_identifier': get_av_number(obj['instances']),
                'number_of_units': 1,
                'program_unique_identifier': get_av_number(obj['instances']),
                'original_format': get_format(obj['notes'], client),
                'original_recording_date': get_date(obj['dates']),
                'title': get_title(obj),
                'series': get_parent(top_containers),
                'file_name_root': obj['ref_id'],
                'notes_to_engineer_speed': '',
                'notes_to_engineer': '',
                'format_specific_notes_tape': '',
                'format_specific_notes': '',
                'audio_reel_size': '',
            }
        else:
            yield {
                'box_number': get_box_number(top_containers),
                'folder_number': get_folder_number(obj['instances']),
                'title': get_title(obj),
                'filename': obj['ref_id']
            }

def main(output_filename, format, object, series, file):
    client = ASpace().client
    if object:
        print(f"Fetching data for archival object {object}.")
        data = [object_data(object, client)]
    elif series:
        print(f"Fetching data for children of archival object {series}.")
        data = series_data(series, client)
    else:
        print(f"Fetching data about all archival objects in file {file}.")
        if not Path(file).is_file():
            raise FileNotFoundError(f'The input file {file} could not be found')
        ref_ids = parse_input_file(file)
        data = [object_data(ref_id, client) for ref_id in ref_ids]
    formatted = format_data(data, format, client)
    normalized_output = format_output_filename(output_filename)
    already_exists = Path(normalized_output).is_file()
    with open(normalized_output, 'a') as csv_file:
        fieldnames = AV_FIELDNAMES if format == 'av' else TEXT_FIELDNAMES
        writer = DictWriter(csv_file, fieldnames=fieldnames)
        if not already_exists:
            writer.writerow(fieldnames)
        print(f"Writing data to {normalized_output}.")
        for object in formatted:
            writer.writerow(object)
        print("Done.")


if __name__ == '__main__':
    parser = ArgumentParser(description='Creates or updates a digitization manifest.')
    parser.add_argument(
        'output_filename',
        help='File path for the manifest.')
    parser.add_argument(
        'format',
        choices=['av', 'text'],
        help='The format of the materials to be digitized.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--object',
        help='ArchivesSpace RefID for an archival object to add to the manifest.')
    group.add_argument(
        '--series',
        help='ArchivesSpace RefID for a series containing archival objects to add to the manifest.')
    group.add_argument(
        '--file',
        help='File containing a list of comma-separated ArchivesSpace RefIDs for archival objects to add to the manifest.')
    args = parser.parse_args()
    main(args.output_filename, args.format, args.object, args.series, args.file)