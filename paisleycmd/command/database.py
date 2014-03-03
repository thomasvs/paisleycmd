# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

"""
The database command
"""

from twisted.internet import defer

from paisleycmd.extern.command import tcommand

from paisleycmd.common import logcommand
from paisleycmd.common import common
from paisleycmd.command import view


class Clean(tcommand.TwistedCommand):

    description = """Clean old views for a database."""

    @defer.inlineCallbacks
    def doLater(self, args):
        if not args:
            self.stderr.write('Please give database name to clean.\n')
            defer.returnValue(3)
            return

        d = self.parentCommand.parentCommand.db.cleanDB(args[0])
        d.addErrback(common.errback, self)

        yield d

class Compact(tcommand.TwistedCommand):

    description = """Compact a database."""

    @defer.inlineCallbacks
    def doLater(self, args):
        if not args:
            db = self.getRootCommand().getDatabase()
        else:
            db = args[0]
        if not db:
            self.stderr.write('Please give database name to compact.\n')
            defer.returnValue(3)
            return

        d = self.parentCommand.parentCommand.getAdminClient().compactDB(db)
        d.addErrback(common.errback, self)
        yield d


class Create(tcommand.TwistedCommand):

    description = """Create a database."""

    @defer.inlineCallbacks
    def doLater(self, args):
        if not args:
            self.stderr.write('Please give database name to create.\n')
            defer.returnValue(3)
            return

        client = self.getRootCommand().getAdminClient()
        d = client.createDB(args[0])
        d.addErrback(common.errback, self)
        yield d


class List(tcommand.TwistedCommand):

    description = """List databases."""

    @defer.inlineCallbacks
    def doLater(self, args):
        gen = yield self.parentCommand.parentCommand.db.listDB()
        for name in gen:
            self.stdout.write('%s\n' % name)

class Database(logcommand.LogCommand):

    subCommandClasses = [Clean, Compact, Create, List, view.View]

    aliases = ['db', ]

    description = 'Interact with databases.'
