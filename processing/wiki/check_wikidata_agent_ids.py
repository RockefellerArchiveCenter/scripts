#!/usr/bin/env python3

# Checks Wikidata identifiers for agents in ArchivesSpace to see if they have been redirected.
# Reports errors with identifiers that are missing in Wikidata. If these errors are reported,
# they should be fixed first and then the script should be re-run.

import json
import traceback
from urllib3.util import Retry

from asnake.aspace import ASpace
from requests import adapters, exceptions, Session


class WikidataClient(object):

    def __init__(self):
        """Sets up retries and backoffs to avoid Wikidata API rate limiting."""
        self.session = Session()
        self.session.headers['User-Agent'] = 'wikidata-id-checker/v1'
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[502, 503, 504, 429],
            allowed_methods={'GET'},
        )
        self.session.mount("https://", adapters.HTTPAdapter(max_retries=retries))

    def get(self, url, **kwargs):
        return self.session.get(url, **kwargs)
        

def main():
    """Main method which calls all other functions."""
    as_client = ASpace().client
    wikidata_client = WikidataClient()

    wikidata_ids = get_wikidata_ids(as_client)    
    redirects = check_wikidata_ids(wikidata_ids, wikidata_client)

    if redirects:
        print("\n\nThe following identifiers were redirected:")
        for r in redirects:
            print(f"\t{r['from']} now redirects to {r['to']}")


def get_wikidata_ids(as_client):
    """Gets a list of Wikidata IDs stored in ArchivesSpace.
    
    This search is a little ham-fisted in that it searches all agent records
    for strings that start with Q. This works because all Wikidata identifiers
    for entities start with the letter Q. A better approach would be to search
    for all agent records which have `wikidata` as a source for one of the 
    `agent_record_identifier` ID sets.
    """
    params = {
        "q": "Q*",
        "fields[]": "json",
        "type[]": "agent",
        "page": "1",
    }
    wikidata_ids = []
    print("Getting agent data from ArchivesSpace")
    for res in as_client.get_paged("/repositories/2/search", params=params):
        agent = json.loads(res['json'])
        wikidata_id = parse_wikidata_id(agent)
        if wikidata_id:
            wikidata_ids.append(wikidata_id)
    return wikidata_ids


def parse_wikidata_id(agent):
    """Parses Wikidata ID from ArchivesSpace agent data."""
    wikidata_id = None
    for id_set in agent.get('agent_record_identifiers', []):
        if id_set['source'] == 'wikidata':
            wikidata_id = id_set['record_identifier']
    return wikidata_id


def check_wikidata_ids(id_list, client):
    """Checks list of Wikidata IDs for redirects.
    
    Missing IDs or other errors in fetching will also be reported.
    If missing IDs are reported, those should be fixed first and then
    the script should be re-run.
    """
    redirects = []
    chunk_size = 50
    print("Getting entity data from Wikidata")
    for i in range(0, len(id_list), chunk_size):
        id_chunk = id_list[i:i + chunk_size]
        try:
            params = {'action': 'wbgetentities', 'ids': '|'.join(id_chunk), 'format': 'json'}
            resp = client.get(f'https://www.wikidata.org/w/api.php', params=params)
            resp.raise_for_status()
            data = resp.json()
            if data.get('error'):
                raise Exception(f"Error fetching ID {data['error']['id']}: {data['error']['info']}")
            for entity_id in data['entities']:
                entity = data['entities'][entity_id]
                if entity.get('redirects'):
                    redirects.append(entity['redirects'])
        except exceptions.HTTPError:
            traceback.print_exc()
        except Exception as e:
            print(e)

    return redirects


if __name__ == '__main__':
    main()