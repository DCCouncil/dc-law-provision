#!/usr/bin/env python
from __future__ import print_function

import os
from contextlib import closing, contextmanager
from universalclient import Client
from datetime import datetime
import requests

INDEX_BULK_URL = 'https://beta.code.dccouncil.us/index.bulk'

DIR = os.path.abspath(os.path.dirname(__file__))

schema_file = os.path.join(DIR, 'schema.json')
etag_file = os.path.join(DIR, 'etag.txt')
cache_file = os.path.join(DIR, 'index.bulk')

def update_index():
    with get_new_data() as is_new:
        if is_new:
            upload_data()

@contextmanager
def get_new_data():
    """
    get the new index.bulk file iff the etag has changed.
    save the new index.bulk to file, return the new etag.
    save the etag to file if no errors
    """
    try:
        with open(etag_file, 'r') as f:
            old_etag = f.read()
    except:
        old_etag = None

    with closing(requests.get(INDEX_BULK_URL, stream=True)) as resp:
        new_etag = resp.headers['etag']
        is_new = True
        if old_etag == new_etag:
            is_new = False
        else:
            is_new = True
            print(datetime.now(), 'starting index of', new_etag)
            with open(cache_file, 'w') as f:
                for block in resp.iter_content(1024):
                    f.write(block)
        try:
            yield is_new
        except Exception as e:
            print(datetime.now(), 'finished index of {} with ERRORS: {}'.format(new_etag, e))
        else:
            if is_new:
                with open(etag_file, 'w') as f:
                    f.write(new_etag)
                print(datetime.now(), 'finished index of', new_etag)

def upload_data():
    """
    do a bulk update using the index.bulk on filesystem;
    """
    es = Client('http://localhost:9200')
    es.dc.DELETE()

    with open(schema_file) as f:
        es.dc.POST(data=f.read())
    with open(cache_file, 'r') as f:
        lines = []
        for line in f:
            lines.append(line)
            if len(lines) >= 10000000 and not len(lines) % 2:
                lines = perform_upload()
        if len(lines):
            perform_upload(es, lines)

def perform_upload(es, lines):
    """
    given a elasticsearch client and a list of lines, perform the bulk insert
    return a new empty lines list
    """
    resp = es._bulk.POST(data=''.join(lines))
    if resp.status_code >= 400:
        raise Exception('HTTP Error {} {}: {} in request starting with line {}'.format(resp.status_code, resp.reason, resp.text, lines[0]))
    resp_body = resp.json()
    if resp_body['errors']:
        import pdb
        pdb.set_trace()

if __name__ == '__main__':
    update_index()
