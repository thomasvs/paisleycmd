#!/usr/bin/python
# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

# This is an example of a filter to use for paisley database document delete

# This filter deletes all docs of type thing whose id does not start with thing
# I used this after doing an apply of mushin-hoodie because that peels off the
# top revisions of docs and leaves previous conflicted versions behind

# Sample run:
# paisley -D mushin-hoodie document delete --dry-run examples/delete-non-mushin-hoodie.py

import sys

from paisleycmd.extern.paisley import client


def delete(doc):
    if doc['_id'].startswith('_design'):
        return

    if doc.get('type', None) == 'thing':
            if not doc['_id'].startswith('thing/'):
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
