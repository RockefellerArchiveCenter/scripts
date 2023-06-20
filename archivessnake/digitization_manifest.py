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
#   --file RESOURCE  ArchivesSpace identifier for a resource containing archival
#                    objects to add to the manifest.

from csv import DictWriter
from argparse import ArgumentParser
from os.path import splitext
from pathlib import Path

from asnake.aspace import ASpace
from asnake.utils import format_resource_id, get_note_text, walk_tree

REPO_ID = 2

TEXT_FIELDNAMES = {
            "resource_id": "Resource ID",
            "series": "Series",
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
        raise Exception(f'Expecting to get only one result for ref id {ref_id} but got {len(results["archival_objects"])} instead.')
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

def resource_data(resource_id, client):
    """Fetches data about archival objects contained within a resource.
    
    Args:
        resource_id (str): identifier for a resource
        client (asnake.aspace.ASpace instance): ASpace client

    Returns:
        resource_data (generator): List of dictionaries with data about archival objects in the resource.
    """
    resource_uri = f'/repositories/{REPO_ID}/resources/{resource_id}'
    tree = walk_tree(resource_uri, client)
    next(tree) # skip first item, which is the resource.
    return tree

def already_digitized(instances):
    """Determines if a digital object already exists for an object.
    
    Args:
        instances (list): ArchivesSpace instance data.

    Returns:
        already_digitized (bool)
    """
    digital_instances = [v for v in instances if v["instance_type"] == "digital_object"]
    return bool(len(digital_instances))

def instance_matches_format(format, instances):
    """Determines if a given instance type is present in an object's instances.
    
    Args:
        instance_type (string): lowercased instance type to search for.
        instances (list): ArchivesSpace instance data.

    Returns:
        has_instance_type (bool)
    """
    normalized_format = f"{format.replace('_', ' ')}"
    if normalized_format == 'text':
        return True
    else:
        found = [instance for instance in instances if instance.get('instance_type', '').lower() == normalized_format]
        return bool(len(found))

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

def get_series_path(ancestors, client):
    """Return series path for object.
    
    Args:
        ancestors (list): ArchivesSpace ancestors data.

    Returns:
        series_path (str): Series path of the archival object.
    """
    ancestors.pop()
    resolved_ancestors = [client.get(a['ref']).json() for a in ancestors]
    return ' > '.join([r['title'] for r in reversed(resolved_ancestors)])
    

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
        if not already_digitized(obj['instances']) and instance_matches_format(format, obj['instances']):
            if format in ['audio', 'moving_images']:
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
                    'series': get_series_path(obj['ancestors'], client),
                    'file_name_root': obj['ref_id'],
                    'notes_to_engineer_speed': '',
                    'notes_to_engineer': '',
                    'format_specific_notes_tape': '',
                    'format_specific_notes': '',
                    'audio_reel_size': '',
                }
            else:
                yield {
                    'resource_id': format_resource_id(obj['resource']['ref'], client),
                    'series': get_series_path(obj['ancestors'], client),
                    'box_number': get_box_number(top_containers),
                    'folder_number': get_folder_number(obj['instances']),
                    'title': get_title(obj),
                    'filename': obj['ref_id']
                }

def main(output_filename, format, object, series, resource):
    client = ASpace().client
    if object:
        print(f"Fetching data for archival object {object}.")
        data = [object_data(object, client)]
    elif series:
        print(f"Fetching data for children of archival object {series}.")
        data = series_data(series, client)
    elif resource:
        print(f"Fetching data for children of resource {resource}.")
        data = resource_data(resource, client)
    formatted = format_data(data, format, client)
    normalized_filename = format_output_filename(output_filename)
    already_exists = Path(normalized_filename).is_file()
    with open(normalized_filename, 'a') as csv_file:
        fieldnames = AV_FIELDNAMES if format in ['audio', 'moving_images'] else TEXT_FIELDNAMES
        writer = DictWriter(csv_file, fieldnames=fieldnames)
        if not already_exists:
            writer.writerow(fieldnames)
        print(f"Writing data to {normalized_filename}.")
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
        choices=['audio', 'moving_images', 'text'],
        help='The format of the materials to be digitized.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--object',
        help='ArchivesSpace RefID for an archival object to add to the manifest.')
    group.add_argument(
        '--series',
        help='ArchivesSpace RefID for a series containing archival objects to add to the manifest.')
    group.add_argument(
        '--resource',
        help='ArchivesSpace resource record ID containing archival objects to add to the manifest.')
    args = parser.parse_args()
    main(args.output_filename, args.format, args.object, args.series, args.resource)