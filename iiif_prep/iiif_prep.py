import argparse

from iiif_prep.preparer import Preparer


def main():
    parser = argparse.ArgumentParser(
        description="Copies files from an RF or GEB officer's diary to a new location with ref_ids as directory names")
    parser.add_argument(
        "source_directory",
        help="A directory containing subdirectories of digitized officers diaries.")
    parser.add_argument(
        "target_directory",
        help="A directory in which to create subdirectories and copy TIFFs.")
    args = parser.parse_args()
    Preparer().run(
        args.source_directory,
        args.target_directory)


if __name__ == "__main__":
    main()
