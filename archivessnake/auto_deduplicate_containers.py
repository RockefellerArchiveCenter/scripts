#!/usr/bin/env python3

import argparse
import json

from asnake.aspace import ASpace

AS_REPOSITORY_ID = 2

def is_target(top_container):
	"""Determines if a top container should be the target of a merge."""
	if '.' not in top_container.get('barcode', ''):
		return True
	else:
		return False

def merge_containers(container, client):
	"""Merges top containers."""
	resp = client.post(f'merge_requests/top_container?repo_id={AS_REPOSITORY_ID}', json=container)
	if resp.status_code != 200:
		raise Exception(resp.status_code, resp.text)
	print(f"Top containers {' '.join(c['ref'] for c in container['victims'])} merged into {container['target']['ref']}")

def main(resource_id):
	duplicates = {}
	client = ASpace().client
	escaped_uri = f"\/repositories\/{AS_REPOSITORY_ID}\/resources\/{resource_id}"
	for result in client.get_paged(f"/repositories/{AS_REPOSITORY_ID}/search?q=collection_uri_u_sstr:{escaped_uri}&type[]=top_container&fields[]=json"):
		top_container = json.loads(result['json'])
		container_key = f"{top_container['type']}{top_container['indicator']}"
		if not duplicates.get(container_key):
			duplicates[container_key] = {'target': {}, 'victims': []}
		if is_target(top_container):
			if duplicates[container_key]['target'].get('ref'):
				raise Exception(f"Value for duplicates[{container_key}]['target] already exists: {duplicates[container_key]['target']}")
			duplicates[container_key]['target']['ref'] = top_container['uri']
		else:
			duplicates[container_key]['victims'].append({'ref': top_container['uri']})

	for container in duplicates:
		if duplicates[container].get('victims'):
			if duplicates[container].get('target'):
				merge_containers(duplicates[container], client)
			else:
				print(f"No target for victims {duplicates[container]['victims']}")

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Merges duplicate top_containers in a resource record.')
	parser.add_argument('resource_id', help='ID for an ArchivesSpace resource record')
	args = parser.parse_args()
	main(args.resource_id)