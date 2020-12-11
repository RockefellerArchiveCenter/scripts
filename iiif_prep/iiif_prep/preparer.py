from configparser import ConfigParser
from os import listdir
from os.path import isdir, join

from .archivesspace import ArchivesSpaceClient

# TO DO: add officers (including other directory names) to ignore in
# config setting


class Preparer():
    def run(self, source_directory, target_directory):
        as_client = ArchivesSpaceClient(
            self.config.get("ArchivesSpace", "baseurl"),
            self.config.get("ArchivesSpace", "username"),
            self.config.get("ArchivesSpace", "password"),
            self.config.get("ArchivesSpace", "repository"))
        officers = sorted(self.get_officers)
        for officer in officers:
            officer_path = join(source_directory, officer)
            structure = self.determine_structure(officer_path, officer)
            diaries = self.get_list_of_diaries(officer_path)

    # get officers
    def get_officers(self, source_directory):
        """docstring for get_officers"""
        return [
            d for d in listdir(source_directory) if isdir(
                join(
                    source_directory,
                    d))]

    def determine_structure(self, officer_path, officer):
        """docstring for find_mezzanine_directory"""
        structure = None
        if "TIFFs" in listdir(officer_path):
            structure = "CURRENT"
        elif "Roll" in str(listdir(officer_path)):
            structure = "MICROFILM"
        elif officer in listdir(officer_path)[0].split('_', 1)[0]:
            structure = "LEGACY"
        else:
            raise Exception(
                "{} does not conform to standard structure".format(officer))
        return structure

    def get_list_of_diaries(self, officer_path, structure):
        """Returns name that matches PDF title, and can be used in filepath to mezzanine directory"""
        diaries_list = []
        if structure == "CURRENT":
            mezzanine_directory = join(officer_path, "TIFFs", "Master-Edited")
            diaries_list = [
                d for d in listdir(mezzanine_directory) if isdir(
                    join(
                        mezzanine_directory,
                        d))]
        elif structure == "LEGACY":
            diaries_list = [d for d in listdir(officer_path) if isdir(join(officer_path, d))]
        elif structure == "MICROFILM":
            tiff_directory = [d for d in listdir(officer_path) if "Tiff" in d]
            diaries_list = [d for d in listdir(join(officer_path, tiff_directory[0])) if isdir(join(officer_path, tiff_directory[0], d))]
        return diaries_list
        
    def get_refids(self, officer, diaries_list):
        """docstring for get_refids"""
        pass

    # get path to diary mezzanine files

    # MAYBE get path to diary service pdf (for refid matching)

    # match diary files to refid
