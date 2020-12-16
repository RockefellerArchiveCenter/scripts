# IIIF Prep

Copy digitized mezzanine TIFF files (of GEB and RF Officers Diaries) to a new location with ArchivesSpace ref_ids as directory names, as expected in the RAC IIIF Pipeline.



## Requirements

The entire suite has the following system dependencies:
- Python 3 (tested on Python 3.8)
- ArchivesSnake (Python library)

## Usage

`iiif_prep.py` requires the following arguments:

* `source_directory`: Path to directory containing subdirectories that correspond to RF and GEB "officers." Subdirectories are expected to be structured 3 different ways, which correspond to the three phases of digitization.
* `target_directory`: Path to directory to which mezzanine TIFF files should be copied.


## Configuration

This script requires a `local_settings.cfg` file. For an example of the sections and keys required, see [local_settings.cfg.example](local_settings.cfg.example) in this repository


## Tests

This library comes with unit tests. To quickly run tests, run `tox` from this directory.
