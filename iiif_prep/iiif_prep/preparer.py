import logging

from configparser import ConfigParser
from os import listdir
from os.path import isdir, join
from shutil import copytree

from .archivesspace import ArchivesSpaceClient

# TO DO: add officers (including other directory names) to ignore in
# config setting


class Preparer():
    CURRENT = 0
    MICROFILM = 1
    LEGACY = 2

    def __init__(self):
        logging.basicConfig(
            datefmt='%m/%d/%Y %I:%M:%S %p',
            filename='iiif_preparers.log',
            format='%(asctime)s %(message)s',
            level=logging.INFO)
        self.config = ConfigParser()
        self.config.read("local_settings.cfg")

    def run(self, source_directory, target_directory):
        as_client = ArchivesSpaceClient(
            self.config.get("ArchivesSpace", "baseurl"),
            self.config.get("ArchivesSpace", "username"),
            self.config.get("ArchivesSpace", "password"),
            self.config.get("ArchivesSpace", "repository"))
        officers = sorted(self.get_officers(source_directory,
                                            self.config.get("IgnoreList", "ignore_list")))
        for officer in officers:
            self.officer_path = join(source_directory, officer)
            self.structure = self.determine_structure(officer)
            diaries = self.get_list_of_diaries()
            logging.info("Starting {}. {} diaries to process.".format(
                officer, len(diaries)))
            for d in diaries:
                refid = as_client.get_diary_refid(d)
                mezzanine_directory = self.get_mezzanine_path(officer, d)
                destination = join(target_directory, refid, "master")
                copytree(mezzanine_directory, destination)

    # TODO: ADD LIST OF SUBDIRECTORIES TO IGNORE
    def get_officers(self, source_directory, ignore_list):
        """Gets list of subdirectories, corresponding to "Officers", in a directory.

        Args:
            source_dir (str): A directory containing subdirectoriess for RF and GEB Officers Diaries.
        Returns:
            officers (list): A list of subdirectories
        """
        subdirectories = [
            d for d in listdir(source_directory) if isdir(
                join(
                    source_directory,
                    d))]
        return [s for s in subdirectories if s not in ignore_list]
        [f for f in files if f.startswith(prefix)]

    def determine_structure(self, officer):
        """docstring for find_mezzanine_directory"""
        structure = None
        if "TIFFs" in listdir(self.officer_path):
            structure = self.CURRENT
        elif "Roll" in str(listdir(self.officer_path)):
            structure = self.MICROFILM
        elif officer in listdir(self.officer_path)[0].split('_', 1)[0]:
            structure = self.LEGACY
        else:
            raise Exception(
                "{} does not conform to standard structure".format(officer))
        return structure

    def get_list_of_diaries(self):
        """Returns name that matches PDF title, and can be used in filepath to mezzanine directory"""
        diaries_list = []
        if self.structure == self.CURRENT:
            mezzanine_directory = join(
                self.officer_path, "TIFFs", "Master-Edited")
            diaries_list = [
                d for d in listdir(mezzanine_directory) if isdir(
                    join(
                        mezzanine_directory,
                        d))]
        elif self.structure == self.LEGACY:
            diaries_list = [d for d in listdir(
                self.officer_path) if isdir(join(self.officer_path, d))]
        elif self.structure == self.MICROFILM:
            tiff_directory = [d for d in listdir(
                self.officer_path) if "tiff" in d.lower()]
            diaries_list = [
                d for d in listdir(
                    join(
                        self.officer_path,
                        tiff_directory[0])) if isdir(
                    join(
                        self.officer_path,
                        tiff_directory[0],
                        d))]
        return diaries_list

    def get_mezzanine_path(self, officer, diary):
        """Return path to mezzanine TIFF files for a diary"""
        mezzanine_directory = None
        if self.structure == self.CURRENT:
            mezzanine_directory = join(
                self.officer_path, "TIFFs", "Master-Edited", diary)
        elif self.structure == self.LEGACY:
            mezzanine_directory = join(
                self.officer_path, diary, "Master_Edited")
        elif self.structure == self.MICROFILM:
            tiff_directory = [d for d in listdir(
                self.officer_path) if "Tiff" in d]
            mezzanine_directory = join(
                self.officer_path, tiff_directory[0], diary)
        return mezzanine_directory

    # get path to diary mezzanine files

    # MAYBE get path to diary service pdf (for refid matching)

    # match diary files to refid
