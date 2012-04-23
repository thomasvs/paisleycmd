# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

"""
The view command
"""

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

    subCommandClasses = [List, Size]

    description = 'Interact with views.'
