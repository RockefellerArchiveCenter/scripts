#!/usr/bin/env python3

"""
Moves open catalogued collections to open directory, and copies to Virtual Vault. 

To use, first connect to the X Drive, then pass in the following arguments:
    - the root directory containing Cataloged Reports. The script expects 
      two subdirectories in this directory, named `open` and `restricted`, 
      both of which contain catalogued reportd named by AS refid.
    - the directory into which open reports should be uploaded to be transferred
      to the Virtual Vault, i.e. the `catalogued-reports` subdirectory in the 
      top-level `VirtualVault` directory.
"""

import argparse
from shutil import copy2
from pathlib import Path

REFIDS = [
   
]

def main(reports_dir, virtual_vault_dir):
    for refid in REFIDS:
        closed_path = Path(reports_dir, 'restricted', f'{refid}.pdf')
        virtual_vault_path = Path(virtual_vault_dir, f'{refid}.pdf')
        open_path = Path(reports_dir, 'open', f'{refid}.pdf')
        if closed_path.is_file():
            copy2(closed_path, virtual_vault_path)
            closed_path.rename(open_path)
            print(refid)
        else:
            print(f'Could not find {str(closed_path)}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Moves open catalogued collections to open directory, and copies to Virtual Vault.')
    parser.add_argument('reports_dir', help='Root directory for cataloged reports')
    parser.add_argument('virtual_vault_dir', help='Root directory for virtual vault')
    args = parser.parse_args()
    main(args.reports_dir, args.virtual_vault_dir)