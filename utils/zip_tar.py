#!/usr/bin/env python3

import argparse
import os
import tarfile
import zipfile


class DirectorySerializer(object):
    def __init__(self, source_dir):
        self.base_path = source_dir

    def run(self):
        for f in os.listdir(self.base_path):
            if os.path.isdir(os.path.join(self.base_path, f)):
                self.make_tar(os.path.join(self.base_path, f))
                self.make_targz(os.path.join(self.base_path, f))
                self.make_zip(os.path.join(self.base_path, f))

    def get_filepath(self, dir, ext):
        output_filename = "{}.{}".format(os.path.basename(dir), ext)
        return os.path.join(self.base_path, output_filename)

    def make_zip(self, dir):
        with zipfile.ZipFile(self.get_filepath(dir, "zip"), "w") as zip:
            for folder, subfolders, filenames in os.walk(dir):
                for f in filenames:
                    filepath = os.path.join(folder, f)
                    zip.write(
                        filepath,
                        arcname=os.path.join(
                            os.path.basename(dir),
                            filepath.replace(dir, "").lstrip("/")))

    def make_tar(self, dir):
        with tarfile.open(self.get_filepath(dir, "tar"), "w") as tar:
            tar.add(dir, arcname=os.path.basename(dir))

    def make_targz(self, dir):
        with tarfile.open(self.get_filepath(dir, "tar.gz"), "w:gz") as tar:
            tar.add(dir, arcname=os.path.basename(dir))


parser = argparse.ArgumentParser(description='Creates ZIP and TAR files from a list of directories.')
parser.add_argument('filepath', help='File path of JSON file to split into separate files.')
args = parser.parse_args()


DirectorySerializer(args.filepath).run()
