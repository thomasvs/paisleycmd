#!/usr/bin/python
# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

# This is an example of a filter to use for paisley database document apply
# Sample run:
# paisley -D daddup document apply --dry-run examples/apply-removename.py

import sys

from paisleycmd.extern.paisley import client


def update(doc):
    if doc.get('type', None) != 'track':
        return

    if not doc.get('name', None):
        return

    found = False
    for fragment in doc.get('fragments', []):
        if fragment.get('chroma'):
            if fragment['chroma'].get('title'):
                found = True
        for file in fragment.get('files', []):
            if file.get('metadata'):
                if file['metadata'].get('title'):
                    found = True

    if found:
        doc['name'] = None
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
