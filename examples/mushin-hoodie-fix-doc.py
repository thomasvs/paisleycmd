#!/usr/bin/python
# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

# This is an example of a filter to use for paisley database document apply
#
# This script fixes documents based on bugs noticed:
#
# - ensures that all urgency and importance fields are integers, not
#   strings.  mushin-hoodie was inaccurately saving these as strings on
#   modifications.
#
# - fix broken due dates like 2009-11-15T00:00:00Z161049600000
#
# Sample run:
# paisley -D daddup document apply --dry-run examples/mushin-hoodie-fix-doc.py

import sys

from paisleycmd.extern.paisley import client


def intifyKey(doc, key):
    if key not in doc:
        return

    if type(doc[key]) in (str, unicode):
        doc[key] = int(doc[key])
        return True


def fixDate(doc, key):
    # handles both non-existent keys and None values
    if not doc.get(key, None):
        return

    pos = doc[key].find('Z', 0, -1)
    if pos > -1:
        doc[key] = doc[key][:pos + 1]
        return True


def update(doc):

    updated = False

    # only look at things
    if not doc['_id'].startswith('thing/'):
        return

    if doc.get('type', None) != 'thing':
        return


    # fix importance/urgency
    if intifyKey(doc, 'importance'):
        updated = True

    if intifyKey(doc, 'urgency'):
        updated = True

    # fix due date
    if fixDate(doc, 'due'):
        updated = True

    if fixDate(doc, 'start'):
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
