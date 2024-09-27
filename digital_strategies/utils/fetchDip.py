#! usr/bin/env python

# fetch_dip.py
# This script is designed to be run at regular intervals, for example from a crontab.
#
# Downloads a DIP from Archivematica to the TMP_DIR and extracts the tarball.
# Derivatives are created for each file in its objects directory, and they are moved,
# along with the original file, to the DESTINATION_DIR.
#
# Tested on Python 3.7.0. Requires Python requests library (http://docs.python-requests.org/en/master/)
# and Imagemagick with Ghostscript ()

import glob
import json
import logging
import os
import requests
import shutil
import subprocess
import tarfile

# Logging
LOG_FILE = 'fetch-dip-log.txt'
LOG_LEVEL = 'INFO'
# System locations
DESTINATION_DIR = '/am/dest/'
TMP_DIR = '/am/tmp/'
# File to store UUIDs of already-downloaded DIPs
DOWNLOADED_DIPS_FILE = '/am/downloads.json'
# Archivematica configs
ARCHIVEMATICA_USERNAME = 'user'
ARCHIVEMATICA_API_KEY = 'apikey'
ARCHIVEMATICA_HEADERS = {"Authorization": "ApiKey {}:{}".format(ARCHIVEMATICA_USERNAME, ARCHIVEMATICA_API_KEY)}
ARCHIVEMATICA_BASEURL = 'http://archivematica-storage-service-url:port/api/v2/'
ARCHIVEMATICA_PIPELINE_UUID = 'pipeline-uuid'

logging.basicConfig(filename=LOG_FILE, format='%(asctime)s %(message)s', level=getattr(logging, LOG_LEVEL))


class ArchivematicaClientError(Exception): pass


class DIPFetcherError(Exception): pass


class DIPFetcher():
    def __init__(self):
        self.tmp = TMP_DIR
        self.dest = DESTINATION_DIR
        self.client = ArchivematicaClient()
        self.downloads = DOWNLOADED_DIPS_FILE
        for dir in [self.tmp, self.dest]:
            if not os.path.isdir(dir):
                raise DIPFetcherError("{} must be created".format(dir))
        if not os.path.isfile(self.downloads):
            raise DIPFetcherError("{} must be created".format(self.downloads))
        try:
            open(self.downloads, 'r')
        except json.decoder.JSONDecodeError:
            raise DIPFetcherError("{} is not valid JSON".format(self.downloads))
            

    def run(self):
        logging.info('*** Starting routine ***')
        package_count = 0

        # Load list of previously downloaded DIPs from external file
        with open(self.downloads, 'r') as f:
            downloaded_list = json.load(f)

        for package in self.client.retrieve_paged('file/', params={'package_type': 'DIP'}):
            if (package['origin_pipeline'].split('/')[-2] == ARCHIVEMATICA_PIPELINE_UUID) and (package['uuid'] not in downloaded_list):
                self.uuid = package['uuid']
                try:
                    self.download_package(package)
                    self.extract_objects(os.path.join(self.tmp, "{}.tar".format(self.uuid)), self.tmp)
                    downloaded_list.append(self.uuid)
                    self.make_derivatives()
                    self.move_files()
                    self.cleanup()
                    package_count += 1
                except Exception as e:
                    logging.error(e)
                    continue

        # Dump updated list of downloaded packages to external file
        with open(self.downloads, 'w') as f:
            json.dump(downloaded_list, f)

        logging.info('*** Routine complete. {} DIPs downloaded and processed ***'.format(package_count))

    def make_derivatives(self):
        logging.debug("Creating derivatives for {}".format(self.uuid))
        for object in self.objects:
            commands = (
             ('Thumbnail with a height of 100px', "convert {}[0] -thumbnail 'x100' `echo {}`".format(object, "{}_thumb.jpg".format(os.path.splitext(object)[0]))),
             ('Square thumbnail 75x75 px', "convert {}[0] -thumbnail '75x75^' -gravity 'Center' -crop '75x75+0+0' `echo {}`".format(object, "{}_thumb75.jpg".format(os.path.splitext(object)[0]))),
             ('Square thumbnail 300x300 px', "convert {}[0] -thumbnail '300x300^' -gravity 'Center' -crop '300x300+0+0' `echo {}`".format(object, "{}_thumb300.jpg".format(os.path.splitext(object)[0]))),
             ('File with proportions of 1.9w to 1h', "convert {}[0] -gravity 'North' -crop '100%x53%+0+0' `echo {}`".format(object, "{}_thumbfb.jpg".format(os.path.splitext(object)[0]))),
            )
            for cmd in commands:
                logging.debug(cmd[0])
                proc = subprocess.Popen(cmd[1], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                while True:
                    next_line = proc.stdout.readline().decode("utf-8")
                    if not next_line:
                        break
                    logging.debug(next_line)

                ecode = proc.wait()
                if ecode != 0:
                    continue

    def move_files(self):
        for obj in self.objects:
            for f in glob.glob("{}*".format(os.path.splitext(obj)[0])):
                logging.debug("Moving {} to {}".format(f, self.dest))
                os.rename(f, os.path.join(self.dest, os.path.basename(f)))

    def download_package(self, package_json):
        logging.debug("Downloading {}".format(self.uuid))
        response = self.client.retrieve('/file/{}/download/'.format(self.uuid), stream=True)
        extension = os.path.splitext(package_json['current_path'])[1]
        if not extension:
            extension = '.tar'
        with open(os.path.join(self.tmp, '{}{}'.format(self.uuid, extension)), "wb") as package:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    package.write(chunk)
        return package

    def extract_objects(self, archive, dest):
        logging.debug("Extracting {}".format(self.uuid))
        self.objects = []
        ext = os.path.splitext(archive)[1]
        if ext == '.tar':
            tf = tarfile.open(archive, 'r')
            tf.extractall(dest)
            for member in tf.members:
                if 'objects/' in member.name:
                    os.rename(os.path.join(dest, member.name), os.path.join(dest, os.path.basename(member.name)))
                    self.objects.append(os.path.join(dest, os.path.basename(member.name)))
            tf.close()
        else:
            raise DIPFetcherError("Unrecognized archive extension", ext)
        return dest

    def cleanup(self):
        logging.debug("Cleaning up {}".format(self.tmp))
        for d in os.listdir(self.tmp):
            file_path = os.path.join(self.tmp, d)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)


class ArchivematicaClient(object):
    def __init__(self):
        self.username = ARCHIVEMATICA_USERNAME
        self.api_key = ARCHIVEMATICA_API_KEY
        self.headers = ARCHIVEMATICA_HEADERS
        self.baseurl = ARCHIVEMATICA_BASEURL

    def retrieve(self, uri, *args, **kwargs):
        full_url = "/".join([self.baseurl.rstrip("/"), uri.lstrip("/")])
        response = requests.get(full_url, headers=self.headers, *args, **kwargs)
        if response:
            return response
        else:
            raise ArchivematicaClientError("Could not return a valid response for {}".format(full_url))

    def retrieve_paged(self, uri, *args, limit=10, **kwargs):
        full_url = "/".join([self.baseurl.rstrip("/"), uri.lstrip("/")])
        params = {"limit": limit, "offset": 0}
        if "params" in kwargs:
            params.update(**kwargs['params'])
            del kwargs['params']

        current_page = requests.get(full_url, params=params, headers=self.headers, **kwargs)
        if not current_page:
            raise ArchivematicaClientError("Authentication error while retrieving {}".format(full_url))
        current_json = current_page.json()
        if current_json.get('meta'):
            while current_json['meta']['offset'] <= current_json['meta']['total_count']:
                for obj in current_json['objects']:
                    yield obj
                if not current_json['meta']['next']: break
                params['offset'] += limit
                current_page = requests.get(full_url, params=params, headers=self.headers, **kwargs)
                current_json = current_page.json()
        else:
            raise ArchivematicaClientError("retrieve_paged doesn't know how to handle {}".format(full_url))

DIPFetcher().run()
