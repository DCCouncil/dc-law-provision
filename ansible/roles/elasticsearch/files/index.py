#!/usr/bin/env python
from __future__ import print_function

import os
from contextlib import closing
from universalclient import Client
from datetime import datetime
import requests

DIR = os.path.abspath(os.path.dirname(__file__))

schema_file = os.path.join(DIR, 'schema.json')
etag_file = os.path.join(DIR, 'etag.txt')
cache_file = os.path.join(DIR, 'index.bulk')

def update_index():
    try:
        with open(etag_file, 'r') as f:
            old_etag = f.read()
    except:
        old_etag = None

    with closing(requests.get('https://beta.code.dccouncil.us/index.bulk', stream=True)) as resp:
        new_etag = resp.headers['etag']
        if old_etag == new_etag:
            return
        print(datetime.now(), 'starting index of', new_etag)
        with open(cache_file, 'w') as f:
            for block in resp.iter_content(1024):
                f.write(block)

    es = Client('http://localhost:9200')
    es.dc.DELETE()
    with open(schema_file) as f:
        es.dc.POST(data=f.read())
    with open(cache_file, 'r') as f:
        while True:
            lines = f.readlines(10000000)
            if not lines:
                break
            resp = es._bulk.POST(data=''.join(lines))
            # need to handle errors
    with open(etag_file, 'w') as f:
        f.write(new_etag)
    print(datetime.now(), 'finished index of', new_etag)

if __name__ == '__main__':
    update_index()
