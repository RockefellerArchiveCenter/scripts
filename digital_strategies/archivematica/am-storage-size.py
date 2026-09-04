#!/usr/bin/env python3

# Parse AIPs to determine total size of digitized image and born-digital AIPs

import requests

AV_LOCATION = '467dcf2f-38bd-4352-9d26-9c42a6d097da'
ZODIAC_PIPELINE = '48e40ff9-1123-4759-a6df-f06121a276e7'
MAIN_PIPELINE = 'defea6ec-6c5e-4bdd-9f4f-704264e6dea6'

STORAGE_SERVICE_URL = ''
STORAGE_SERVICE_USER_NAME = ''
STORAGE_SERVICE_API_KEY = ''

def main():
    
    image_size = 0
    bd_size = 0
    image_count = 0
    bd_count = 0

    initial_page = requests.get(
        f"{STORAGE_SERVICE_URL}/api/v2/file", 
        params={"username": STORAGE_SERVICE_USER_NAME, "api_key": STORAGE_SERVICE_API_KEY, "package_type": "AIP"}).json()
    image_size, bd_size, image_count, bd_count = add_sizes(
        initial_page, 
        image_size, 
        bd_size, 
        image_count, 
        bd_count)
    next = initial_page['meta']['next']
    while next:
        print(next)
        url = f"{STORAGE_SERVICE_URL}{next}"
        next_page = requests.get(url).json()
        image_size, bd_size, image_count, bd_count = add_sizes(
            next_page, 
            image_size, 
            bd_size, 
            image_count, 
            bd_count)
        next = next_page['meta']['next']

    print(f'Born digital size: {bd_size / (1024 * 1024 * 1024)}')
    print(f'Born digital count: {bd_count}')
    print(f'Digitized image size: {image_size / (1024 * 1024 * 1024)}')
    print(f'Digitized image count: {image_count}')


def add_sizes(page, image_size, bd_size, image_count, bd_count):
    for aip in page['objects']:
        aip_category = parse_aip_category(aip)
        if aip_category == 'born_digital':
            bd_size += aip['size']
            bd_count += 1
        elif aip_category == 'digitized_image':
            image_size += aip['size']
            image_count += 1
    return image_size, bd_size, image_count, bd_count


def parse_aip_category(aip):
    if aip['current_location'].split('/')[-2] == AV_LOCATION:
        return 'digitized_av'
    elif aip['origin_pipeline'].split('/')[-2] == ZODIAC_PIPELINE:
        return 'born_digital'
    elif aip['origin_pipeline'].split('/')[-2] == MAIN_PIPELINE:
        return 'digitized_image'
    raise Exception(f'Could not parse aip category for aip {aip}')


if __name__ == '__main__':
    main()