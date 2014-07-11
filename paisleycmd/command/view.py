# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

"""
The view command
"""

import base64

from twisted.internet import defer

from paisleycmd.extern.command import command, tcommand
from paisleycmd.extern.paisley.client import json

from paisleycmd.common import logcommand, common


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

class Compact(tcommand.TwistedCommand):

    usage = """[-a] [DESIGN_DOC_NAME]"""
    description = """Compact all views in the given design document.

To see all design documents, use list.  Use the part after _design/ as the
name.
"""
    def addOptions(self):
        self.parser.add_option('-a', '--all',
                          action="store_true", dest="all",
                          help="compact views in all design documents")


    @defer.inlineCallbacks
    def doLater(self, args):
        if not args and not self.options.all:
            self.stderr.write('Please give a design document to compact.\n')
            defer.returnValue(3)
            return

        client = self.getRootCommand().getClient()
        db = self.getRootCommand().getDatabase()

        if self.options.all:
            res = yield _getViews(self)

            for design, views in res.items():
                name = design[len('_design/'):]
                self.stdout.write('Compacting views in design document %s\n' % (
                    name))
                d = client.compactDesignDB(db, name)
                d.addErrback(common.errback, self)
                yield d


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


class Get(tcommand.TwistedCommand):

    usage = "%command -d/--design designname -v/--view viewname"
    description = """Get a view. This triggers indexing if needed."""

    def addOptions(self):
        self.parser.add_option('-d', '--design',
            action="store", dest="design",
            help="name of the design doc (without leading _design/")
        self.parser.add_option('-v', '--view',
            action="store", dest="view",
            help="name of the view")

    def handleOptions(self, options):
        self._options = options

    @defer.inlineCallbacks
    def doLater(self, args):
        if not self._options.design:
            raise command.CommandError(
                "Please specify the name of a design document with -d "
                "(without the leading _design/).")

        if not self._options.view:
            raise command.CommandError(
                "Please specify the name of a view with -v")

        res = yield self.getRootCommand().db.openView(
            self.getRootCommand().getDatabase(),
            self._options.design,
            self._options.view)


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

    summary = "show size used by views"

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

    subCommandClasses = [Compact, Dump, Get, List, Size]

    description = 'Interact with views.'
