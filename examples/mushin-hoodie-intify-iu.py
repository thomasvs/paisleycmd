#!/usr/bin/python
# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

# This is an example of a filter to use for paisley database document apply
#
# This script ensures that all urgency and importance fields are integers, not
# strings.  mushin-hoodie was inaccurately saving these as strings on
# modifications.
#
# Sample run:
# paisley -D daddup document apply --dry-run examples/mushin-hoodie-intify-iu.py

import sys

from paisleycmd.extern.paisley import client


def intifyKey(doc, key):
    if key not in doc:
        return

    if type(doc[key]) in (str, unicode):
        doc[key] = int(doc[key])
        return True

def update(doc):

    updated = False

    # only look at things
    if not doc['_id'].startswith('thing/'):
        return

    if doc.get('type', None) != 'thing':
        return


    if intifyKey(doc, 'importance'):
        updated = True

    if intifyKey(doc, 'urgency'):
        updated = True

    if not updated:
        return

    return doc


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

        ret = update(doc)
        if not ret:
            print
        else:
            # updated, so remove _rev
            # del ret['_rev']
            print client.json.dumps(ret)

        sys.stdout.flush()

if __name__ == '__main__':
    main()
