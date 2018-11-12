# imagemagick

These scripts create thumbnail derivatives of digital objects for use on DIMES, plus additional actions.

## makeThumb.sh

Creates several different derivative thumbnails of digital objects and then moves files from a temporary directory to a web accessible directory.

## makeThumbRepair.sh

Does the same thing as makeThumbs.sh, but is intended to be run once objects have already been moved to web accessible directory.

## Requirements

*   These scripts were written to work on Linux/Mac systems. You cannot run them from the base Windows command line. You can use a tool like Cygwin to emulate the Linux command line on Windows.

## Installation

*   Save these files to the server or file system that contains the digital object derivatives that you want to move/create thumbnails from. You may have to change the directory listings in the scripts.

## Usage

*   Start the script with ./makeThumbs.sh
