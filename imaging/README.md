# Disk Imaging Scripts
Scripts to automate disk imaging for legacy digital media. Developed for use with the BitCurator environment (Linux). In addition to creating a disk image, creates a metadata text file.

`dtc_image.sh` - 3.5" floppy disks using KryoFlux

`optical_disks.sh`- optical disks (excluding audio CDs) using dd

`virus_scan.sh` - scans disk image files (.iso/.img) for viruses using clamscan

`directory_virus_scan.sh` - scans files in a directory for viruses using clamscan

## Requirements
The Sleuth Kit - included in BitCurator environment; to install using Homebrew on Mac use `brew install sleuthkit`

Script for the KryoFlux requires the KryoFlux floppy controller and accompanying software. See http://www.kryoflux.com/

## License
This code is released under an MIT License. See `LICENSE.md` for more information.
