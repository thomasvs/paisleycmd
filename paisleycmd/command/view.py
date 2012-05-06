# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

"""
The view command
"""

import base64

from twisted.internet import defer

from paisleycmd.extern.command import tcommand
from paisleycmd.extern.paisley.client import json

from paisleycmd.common import logcommand


# return: dict of design_doc -> list of view names
@defer.inlineCallbacks
def _getViews(c):
    ret = {}

    res = yield c.getRootCommand().db.listDoc(
        c.getRootCommand().getDatabase(),
        startkey="_design/", endkey="_design0", include_docs=True)

    for row in res['rows']:
        ret[row['key']] = []

        for key, value in row['doc']['views'].items():
            ret[row['key']].append(key)

    defer.returnValue(ret)


class Dump(tcommand.TwistedCommand, logcommand.LogCommand):

    usage = "%command [--key key] docid viewid"
    description = """
Dump view results.

This dumps all documents for the given view in a format that couchdb-load
understands.

"""

    def addOptions(self):
        self.parser.add_option('-k', '--key',
                          action="store", dest="key",
                          help="key to query the view with")

    def handleOptions(self, options):
        self._kwargs = {}

        if options.key:
            self._kwargs['key'] = options.key

        self._kwargs['reduce'] = False
        self._kwargs['include_docs'] = True

    @defer.inlineCallbacks
    def doLater(self, args):
        if not args:
            self.stderr.write('Please specify a design doc and view to dump.\n')
            defer.returnValue(3)
            return

        docId = args[0]
        viewId = args[1]

        self.debug('requesting view in %r %r with kwargs %r',
            docId, viewId, self._kwargs)

        res = yield self.getRootCommand().db.openView(
            self.getRootCommand().getDatabase(), docId, viewId,
            **self._kwargs)

        # adapted from couchdb.tools.dump
        from couchdb.multipart import write_multipart
        envelope = write_multipart(self.stdout, boundary=None)

        for row in res['rows']:
            doc = row['doc']

            print >> self.stderr, 'Dumping document %r' % doc['_id']
            attachments = doc.pop('_attachments', {})
            jsondoc = json.dumps(doc)

            if attachments:
                parts = envelope.open({
                    'Content-ID': doc['_id'],
                    'ETag': '"%s"' % doc['_rev']
                })
                parts.add('application/json', jsondoc)

                for name, info in attachments.items():
                    content_type = info.get('content_type')
                    if content_type is None: # CouchDB < 0.8
                        content_type = info.get('content-type')
                    parts.add(content_type, base64.b64decode(info['data']), {
                        'Content-ID': name
                    })
                parts.close()

            else:
                envelope.add('application/json', jsondoc, {
                    'Content-ID': doc['_id'],
                    'ETag': '"%s"' % doc['_rev']
                }, )

        envelope.close()



class List(tcommand.TwistedCommand):

    description = """List views."""

    @defer.inlineCallbacks
    def doLater(self, args):
        res = yield _getViews(self)

        for design, views in res.items():
            self.stdout.write('%s:\n' % design)
            for view in views:
                self.stdout.write('  %s\n' % view.encode('utf-8'))

class Size(tcommand.TwistedCommand):
    @defer.inlineCallbacks
    def doLater(self, args):
        db = self.getRootCommand().db
        dbName = self.getRootCommand().getDatabase()

        totalRows = 0
        totalSize = 0

        res = yield _getViews(self)

        for design, views in res.items():
            self.stdout.write('%s:\n' % design)
            docId = design[len('_design/'):]

            for view in views:
                content = yield db.openView(dbName, docId, view, reduce=False)

                rows = int(content.get('total_rows', 0))
                size = len(json.dumps(content))

                self.stdout.write('  %50s: %d rows, %d chars\n' % (
                    view.encode('utf-8'), rows, size))
                totalRows += rows
                totalSize += size

        self.stdout.write('total: %d rows, %d chars\n' % (
            totalRows, totalSize))


class View(logcommand.LogCommand):

    subCommandClasses = [Dump, List, Size]

    description = 'Interact with views.'
