## Commonly Used Functions

The following are functions used multiple times in our ArchivesSnake scripts, or that we anticipate re-using.

### Resources, Components, and Description

Use find_by_id endpoint with the refid of an archival object

```
def get_ao(refid):
    # use find_by_id endpoint
    url = 'repositories/2/find_by_id/archival_objects?ref_id[]=' + refid
    ao = client.get(url).json()
    # get archival object as json
    ao_ref = ao.get("archival_objects")[0].get("ref")
    ao = client.get(ao_ref).json()
    return ao
```

Get all notes for an archival object or resource

```
def get_ao_notes(ao):
    # get note type for each note, append to list
    if ao.get("notes"):
        note_list = []
        for n in ao.get("notes"):
            if n.get("type") in ["bioghist", "scopecontent", "relatedmaterial", "separatedmaterial", "phystech", "processinfo", "otherfindaid", "originalsloc", "fileplan", "arrangement"]:
                if n.get("jsonmodel_type") not in ["note_definedlist"]:
                    note_list.append(n.get("subnotes")[0].get("content").replace('\n', ' ').strip())
        return " | ".join(note_list)
    else:
        return ""

```

Get notes of a specific type(s)

```
def get_specific_note(ao, noteType):
    if ao.get("notes"):
        for n in ao.get("notes"):
            if n.get("type") == noteType: #accessrestrict, userestrict
                return n.get("subnotes")[0].get("content").strip().replace('\n', ' ') # replace line break with space

```

Get note contents

```
def getNoteContents(notes, matching_note):
	for note in notes:
		try:
			if note["type"] == matching_note:
				print "found " + note["type"] + " note"
				if note["jsonmodel_type"] == "note_singlepart":
					return note["content"].decode('utf-8')
				else:
					return note["subnotes"][0]["content"].decode('utf-8')		
		except:
			pass
```

Handle archival objects that don't have a title, by either using the display title or the title of parent archival object 

```
def get_title(ao):
    # check if archival object has a title
    if ao.get("title"):
        return ao.get("title")
    # if there's no title, use the title of its immediate ancestor
    else:
        ancestor_url = ao.get("ancestors")[0].get("ref")
        ancestor = client.get(ancestor_url).json()
        return ancestor["title"]
		
    def get_title(self, data):
        try:
            return data.title
        except:
            return data.display_string
```

Get all archival objects from a resource tree

```
for record in self.repo.resources(self.resource_id).tree.walk
```

Get parent resource

```
def findResourceId(headers):
# Gets the parent resource id_0 for each archival object
	try:
		uri = ao["resource"].get('ref')
		resource = (requests.get(resourceURL + str(uri), headers=headers)).json()
		global resourceID
		resourceID = resource["id_0"]
		return resourceID
	except:
		pass
```

#### Dates

Identify whether an archival object is undated

```
def check_undated(ao):
    # ignore date expressions that only consist of some form of undated; will return false for a date expression like "1940, undated"
    if ao.get("dates")[0].get("expression") not in ["n.d.", "undated", "Undated"]:
        return True
    else:
        return False
```

Identify whether there is a structured date

```
def get_end_date(ao):
    # uses either structured date or date expression to get end year
    if ao.get("dates"):
        if find_bulk_dates(ao):
            return find_bulk_dates(ao)
        else:
            # check for structured date field, return date as YYYY-YYYY
            if ao.get("dates")[0].get("begin"):
                return find_year(ao.get("dates")[0].get("end", ao.get("dates")[0].get("begin", "")))
            # if there's no structured date, get date expression
            else:
                if check_undated(ao):
                    if len(ao.get("dates")[0].get("expression")) == 4:
                        return ao.get("dates")[0].get("expression")
                    else:
                        return find_year(ao.get("dates")[0].get("expression"))
                elif get_ancestor(ao):
                    find_ancestor_date(ao)
    elif get_ancestor(ao):
        find_ancestor_date(ao)
```

Get start date

```
def get_start_date(ao):
    # uses structured date to get begin year
    if ao.get("dates"):
        # check for structured date field, return date as YYYY-YYYY
        if ao.get("dates")[0].get("begin"):
            return find_year(ao.get("dates")[0].get("begin", ""))
```

Get end date

```

def get_end_date(ao):
    # uses either structured date or date expression to get end year
    if ao.get("dates"):
        if find_bulk_dates(ao):
            return find_bulk_dates(ao)
        else:
            # check for structured date field, return date as YYYY-YYYY
            if ao.get("dates")[0].get("begin"):
                return find_year(ao.get("dates")[0].get("end", ao.get("dates")[0].get("begin", "")))
            # if there's no structured date, get date expression
            else:
                if check_undated(ao):
                    if len(ao.get("dates")[0].get("expression")) == 4:
                        return ao.get("dates")[0].get("expression")
                    else:
                        return find_year(ao.get("dates")[0].get("expression"))
                elif get_ancestor(ao):
                    find_ancestor_date(ao)
    elif get_ancestor(ao):
        find_ancestor_date(ao)
```

### Instances, Containers, and Locations

Get all instances attached to an archival object

```
    def get_instances(self, instances_array):
        instances = []
        for instance in instances_array:
            top_container = self.aspace.client.get(instance.sub_container.top_container.ref).json()
            instances.append(top_container['display_string'])
        return ", ".join(instances)
```

Get container information, including ID and box and folder #s of an instance

```
def getAvNumber(ao):
    #get top container ref
    container = client.get(ao["instances"][0]["sub_container"]["top_container"]["ref"]).json()
    #get top container indicator
    return container["indicator"]
	
    def get_folders(self, instances_array):
        folders = []
        for instance in instances_array:
            folders.append("{} {}".format(instance.sub_container.type_2, instance.sub_container.indicator_2))
        return ", ".join(folders)
```

Get location
```
def get_location(self, instances_array):
    locations = []
    for instance in instances_array:
        top_container = self.aspace.client.get(instance.sub_container.top_container.ref).json()
        for loc in top_container['container_locations']:
            l = self.aspace.client.get(loc['ref']).json()
            locations.append(l['title'])
    return ", ".join(locations)
```

### What Scripts are Doing

Gather data for analysis - mostly serialized as CSV files

```
column_headings = ["title", "display_string", "dateexpression", "begindate", "enddate", "refid", "accessrestrict"]

column_headings = ['building','floor','room','coordinate_1_label','coordinate_1_indicator','coordinate_2_label','coordinate_2_indicator','uri']

note_list = ['accessrestrict','odd','altformavail','originalsloc','phystech','processinfo','relatedmaterial','separatedmaterial','dimensions','summary','extent','note','physdesc','physloc','materialspec','physfacet',]
column_headings = ['title','resource','level','refid'] + note_list

    column_headings = ['accession date', 'title', 'number', 'container summary',
                       'extent number', 'extent type', 'acquisition type', 'delivery date']
```

Modify or delete notes attached to archival objects

```
def deleteNotes(headers):
# Deletes AccessRestrict notes that match input notecontent
    notes = ao["notes"]
    for index, n in enumerate(notes):
        try:
            if n["type"] == notetype:
                for subnote in n["subnotes"]:
                    if notecontent == subnote["content"]:
                        del notes[index]
                        post = requests.post('{baseURL}'.format(**dictionary) + str(aoId), headers=headers, data=json.dumps(ao))
                        logging.info('Deleted note with ' + str(notecontent) + ' content from archival object ' + str(aoId) + ' in resource ' + str(resourceID))
        except:
            pass

def replaceNotes(headers):
# Deletes AccessRestrict notes that match input notecontent
    notes = ao["notes"]
    for index, n in enumerate(notes):
        try:
            if n["type"] == notetype:
                for subnote in n["subnotes"]:
                    if notecontent == subnote["content"]:
                        subnote["content"] = replacecontent
                        post = requests.post('{baseURL}'.format(**dictionary) + str(aoId), headers=headers, data=json.dumps(ao))
                        logging.info('Replacing note with ' + str(notecontent) + ' content with ' + str(replacecontent) + ' content in archival object ' + str(aoId) + ' in resource ' + str(resourceID))
        except:
            pass
```

Other modifications to archival objects and resources

```
def run(self):
    """Main method for this class, which processes a list of objects."""
    for obj in self.get_objects():
        if (obj.level in self.levels) and (self.is_undated(obj)):
            date = self.calculate_date(obj.uri)
            if date:
                obj_json = obj.json()
                if self.always_add:
                    obj_json['dates'] = [date]
                else:
                    obj_json['dates'].append(date)
                self.save_obj(obj_json)
            print("Cannot calculate dates for {}".format(obj.uri))
```

Modify or delete locations or containers

```
for loc in locs:
    print '/locations/' + str(loc) + ' will be deleted'
    location = (requests.get(locationURL + str(loc), headers=headers)).json()
    deleted = requests.delete(locationURL + str(loc), headers=headers, data=json.dumps(location))
    logging.info('/locations/' + str(loc) + ' was deleted')

def replaceTopContainer(ao, aoId, headers):
	global replaced
	replaced = "0"
	global original
	original ="0"
	if len(ao['instances']) > 0:
		for n, instance in enumerate(ao['instances']):
			if ao["instances"][n]["instance_type"] == "digital_object":
				pass
			elif ao["instances"][n]["sub_container"]["top_container"]["ref"] in replace_dict:
				replaced = ao["instances"][n]["sub_container"]["top_container"]["ref"]
				original = replace_dict[ao["instances"][n]["sub_container"]["top_container"]["ref"]]
				ao["instances"][n]["sub_container"]["top_container"]["ref"] = replace_dict[ao["instances"][n]["sub_container"]["top_container"]["ref"]]
				post = requests.post('{baseURL}'.format(**dictionary) + str(aoId), headers=headers, data=json.dumps(ao))
				print 'Container '+replaced+' was replaced with container '+original+' in archival object '+str(aoId)
				logging.info('Container '+replaced+' was replaced with container '+original+' in archival object '+str(aoId))
			else:
				pass
	else:
		pass

```

Get user input for resources or objects to get data about or to modify
