#!/usr/bin/python
# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

# This is an example of a filter to use for paisley database document apply
# Sample run:
# paisley -D daddup document apply --dry-run examples/apply-removename.py

import sys
import string

from paisleycmd.extern.paisley import client


BASE_16_LIST = string.digits + string.lowercase[0:6]
BASE_16_DICT = dict((c, i) for i, c in enumerate(BASE_16_LIST))
BASE_26_LIST = string.digits + string.lowercase
BASE_26_DICT = dict((c, i) for i, c in enumerate(BASE_16_LIST))

def base_decode(string, reverse_base=BASE_16_DICT):
    length = len(reverse_base)
    ret = 0
    for i, c in enumerate(string[::-1]):
        ret += (length ** i) * reverse_base[c]

    return ret

def base_encode(integer, base=BASE_16_LIST):
    length = len(base)
    ret = ''
    while integer != 0:
        ret = base[integer % length] + ret
        integer /= length

    return ret

def update(doc):
    if doc['_id'].startswith('thing/'):
        return

    if doc.get('type', None) != 'thing':
        return

    doc['createdBy'] = 'xbnjwxg'

    if doc.get('complete', None) == 100:
        doc['state'] = 2
    else:
        doc['state'] = 1

    doc['createdAt'] = doc.get('start', None)
    doc['updatedAt'] = doc.get('updated', None)

    md5 = doc['_id']
    d = base_decode(md5, BASE_16_DICT)
    # fit into 8 hoodie characters
    d %= 26 ** 10
    h = base_encode(d, BASE_26_LIST)
    doc['_id'] = 'thing/' + h[0:9]

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
