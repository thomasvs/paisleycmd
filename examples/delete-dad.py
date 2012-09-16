#!/usr/bin/python
# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

# This is an example of a filter to use for paisley database document delete

# I used this to delete results of an accidental replicate of dad to mushin

# Sample run:
# paisley -D mushin document delete --dry-run examples/delete-dad.py

import sys

from paisleycmd.extern.paisley import client


def delete(doc):
    if doc.get('type', None) in [
        'album',
        'artist',
        'audiofile',
        'track',
        'trackalbum',
        ]:
        return 'DELETE'

    return


def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break

        try:
            doc = client.json.loads(line)
        except:
            print
            continue

        ret = delete(doc)
        if not ret:
            print
        else:
            print ret

        sys.stdout.flush()

if __name__ == '__main__':
    main()
