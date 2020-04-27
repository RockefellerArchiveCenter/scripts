#!/usr/bin/env python3

import argparse
import os
import tarfile
import zipfile


def make_zip(base_path, dir):
    output_filename = "{}.zip".format(os.path.basename(dir))
    output_filepath = os.path.join(base_path, output_filename)
    with zipfile.ZipFile(output_filepath, "w") as zip:
        for folder, subfolders, filenames in os.walk(dir):
            for f in filenames:
                filepath = os.path.join(folder, f)
                zip.write(filepath)


def make_tar(base_path, dir):
    output_filename = "{}.tar".format(os.path.basename(dir))
    output_filepath = os.path.join(base_path, output_filename)
    with tarfile.open(output_filepath, "w") as tar:
        tar.add(dir, arcname=os.path.basename(dir))


def make_targz(base_path, dir):
    output_filename = "{}.tar.gz".format(os.path.basename(dir))
    output_filepath = os.path.join(base_path, output_filename)
    with tarfile.open(output_filepath, "w:gz") as tar:
        tar.add(dir, arcname=os.path.basename(dir))


def main(source_dir):
    for f in os.listdir(source_dir):
        if os.path.isdir(os.path.join(source_dir, f)):
            make_tar(source_dir, os.path.join(source_dir, f))
            make_targz(source_dir, os.path.join(source_dir, f))
            make_zip(source_dir, os.path.join(source_dir, f))


parser = argparse.ArgumentParser(description='Creates ZIP and TAR files from a list of directories.')
parser.add_argument('filepath', help='File path of JSON file to split into separate files.')
args = parser.parse_args()


main(args.filepath)
