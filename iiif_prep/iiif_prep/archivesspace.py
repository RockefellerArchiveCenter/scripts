from string import ascii_lowercase

from asnake.aspace import ASpace

aspace = ASpace(baseurl=baseurl, username=username, password=password)

def find_resource(officer, geb=False):
    if geb:
        resource_id = 146
    elif officer[0].lower() in ascii_lowercase[:5]:
        resource_id = 590
    elif officer[0].lower() in ascii_lowercase[6:12]:
        resource_id = 591
    elif officer[0].lower() in ascii_lowercase[13:18]:
        resource_id = 592
    elif officer[0].lower() in ascii_lowercase[19:]:
        resource_id = 593
    return resource_id

resource_id_list = [146, 590, 591, 592, 593]


def get_all_file_uris(resource_id_list):
    repo=aspace.repositories(2)
    all_file_uris = []
    for resource_id in resource_id_list:
        for record in repo.resources(resource_id).tree.walk:
            # traverse tree of resource record, use level to skip series
            if record.level == "file":
                all_file_uris.append(record.uri)
            
def get_files_with_daos(all_file_uris):
    """docstring for get_files_with_daos"""
    repo=aspace.repositories(2)
    for uri in all_file_uris:
        for uri in list_of_uris:
             obj=aspace.client.get(uri, params={"resolve": ["digital_object"]})
             item_json=obj.json()
             if item_json.get("instances"):
                 for i in item_json.get("instances"):
                     if i.get("instance_type") == "digital_object":
                         dao=i.get("digital_object").get("_resolved")
                         print("{} - {}".format(dao.get("file_versions")
                               [0].get("file_uri"), item_json.get("ref_id")))

def get_diaries(officer, resource_id):
    possible_matches = []
    repo=aspace.repositories(2)
    for record in repo.resources(resource_id).tree.walk:
        if record.level == "subgrp":
            if officer[:4].lower() == record.title[:4].lower():
                possible_matches.append(record.uri)
    print(possible_matches)
    # if len(possible_matches) < 1:
    #     raise Exception("No matches found for {} in resource {}".format(officer, resource_id))
    # elif len(possible_matches) == 1:
    #     officer_uri = possible_matches[0]
    # else:
    #     for match in possible_matches:
    # return officer_uri



resource_id=590
list_of_uris=[]

repo=aspace.repositories(2)
for record in repo.resources(resource_id).tree.walk:
    # traverse tree of resource record, use level to skip series
    if record.level == "file":
        list_of_uris.append(record.uri)

for uri in list_of_uris:
     obj=aspace.client.get(uri, params={"resolve": ["digital_object"]})
     item_json=obj.json()
     if item_json.get("instances"):
         for i in item_json.get("instances"):
             if i.get("instance_type") == "digital_object":
                 dao=i.get("digital_object").get("_resolved")
                 print("{} - {}".format(dao.get("file_versions")
                       [0].get("file_uri"), item_json.get("ref_id")))


    def get_object(ref_id):
        """Gets archival object title and date from an ArchivesSpace refid.

        Args:
            ident (str): an ArchivesSpace refid.
        Returns:
            obj (dict): A dictionary representation of an archival object from ArchivesSpace.
        """
        results=client.get(
            'repositories/{}/find_by_id/archival_objects?ref_id[]={}'.format(repository, ref_id)).json()
        if not results.get("archival_objects"):
            raise Exception(
                "Could not find an ArchivesSpace object matching refid: {}".format(ref_id))
        else:
            obj_ref=results["archival_objects"][0]["ref"]
            obj=client.get(obj_ref).json()
            obj["dates"]=utils.find_closest_value(obj, 'dates', client)
            return format_data(obj)

    def format_data(data):
        """Parses ArchivesSpace data.

        Args:
            data (dict): ArchivesSpace data.
        Returns:
            parsed (dict): Parsed data, with only required fields present.
        """
        title=data.get("title", data.get("display_string")).title()
        dates=", ".join([utils.get_date_display(d, client)
                           for d in data.get("dates", [])])
        return {"title": title, "dates": dates, "uri": data["uri"]}
