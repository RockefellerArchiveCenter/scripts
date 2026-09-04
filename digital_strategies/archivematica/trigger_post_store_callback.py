#!/usr/bin/env python3

from requests import Session

CALLBACK_URL = "https://y12k6u6042.execute-api.us-east-1.amazonaws.com/prod/"

AIPS = [
    # ("package ID", "AIP UUID),
]

def main():
    http = Session()
    http.headers['Content-Type'] = 'application/json'
    for package_id, aip_uuid in AIPS:
        resp = http.post(CALLBACK_URL, json={
                "archivematica_uuid": aip_uuid,
                "package_id": package_id
            })
        resp.raise_for_status()
        print(package_id)


if __name__ =='__main__':
    main()