#!/usr/bin/env python3

# usage: find_data_problems.py [-h] crowley_spreadsheet_path

# Verify data of delivered packages prior to QC

# positional arguments:
#   crowley_spreadsheet_path


import argparse
import configparser

import pandas

def get_crowley_data(spreadsheet_path):
    """Return iterable of iterables with refid, grant_number, reel"""
    data = []
    reel_list = []
    df = pandas.read_excel(spreadsheet_path, header=0)
    for index, row in df.iterrows():
        row_reel = row['Roll Number'].strip()
        reel_list.append(row_reel)
        data.append((row.get('Filename', '').strip(), str(row.get('Grant Number', '')).strip(), row_reel))
    return data, list(set(reel_list))

def get_rac_data(config, reel_list):
    """Return iterable of iterables with refid, grant_number, reel"""
    data = []
    df = pandas.read_excel(config['RAC']['spreadsheet_path'], sheet_name='Reel', header=0)
    df.columns = df.columns.str.strip()
    for index, row in df.iterrows():
        row_reel = str(row['Box']).strip()
        if str(row_reel) in reel_list:
            data.append((row.get('Filename', '').strip(), str(row.get('Grant Number', '')).strip(), row_reel))
    return data

def contents_mismatches(crowley_data, rac_data):
    """
    Verify that contents of a reel are the same in both Crowley and RAC spreadsheets
        If grant is missing from RAC inventory, report that
        If grant is missing from Crowley inventory report that
    """
    errors = []    
    not_in_rac = set(crowley_data) - set(rac_data)
    not_in_crowley = set(rac_data) - set(crowley_data)
    print(rac_data)
    print(crowley_data)
    
    if not_in_rac:
        missing_list = list(not_in_rac)
        sorted_by_reel = sorted(missing_list, key=lambda x: x[2])
        errors.append(f'The following grant(s) in Crowley data do not have an exact match in RAC data:\n')
        for missing_item in sorted_by_reel:
            errors.append(f'\tRefid: {missing_item[0]}\n\tGrant Number: {missing_item[1]}\n\tReel Number: {missing_item[2]}\n\t{missing_item[0]},{missing_item[1]},{missing_item[2]}\n')
    if not_in_crowley:
        missing_list = list(not_in_crowley)
        sorted_by_reel = sorted(missing_list, key=lambda x: x[2])
        errors.append(f'The following grant(s) in RAC data do not have an exact match in Crowley data:\n')
        for missing_item in sorted_by_reel:
            errors.append(f'\tRefid: {missing_item[0]}\n\tGrant Number: {missing_item[1]}\n\tReel Number: {missing_item[2]}\n\t{missing_item[0]},{missing_item[1]},{missing_item[2]}\n')
    return errors

def main(crowley_spreadsheet_path):
    config = configparser.ConfigParser()
    config.read('config.ini')
    crowley_data, reel_list = get_crowley_data(crowley_spreadsheet_path)
    rac_data = get_rac_data(config, reel_list)

    errors = contents_mismatches(crowley_data, rac_data)

    if len(errors):
        print("\n".join(errors))
    else:
        print("No errors found")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Verify data of delivered packages prior to QC")
    parser.add_argument('crowley_spreadsheet_path')
    args = parser.parse_args()
    main(args.crowley_spreadsheet_path)