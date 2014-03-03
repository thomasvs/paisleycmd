# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

"""
The database command
"""

from twisted.internet import defer

from paisleycmd.extern.command import command, tcommand

from paisleycmd.common import logcommand
from paisleycmd.common import common
from paisleycmd.command import view


class _DBCommand(tcommand.TwistedCommand):

    def getDB(self, args, operation=None):
        if not args:
            db = self.getRootCommand().getDatabase()
        else:
            db = args[0]

        if not db:
            if operation:
                msg = 'Please give database name to %s.' % (operation, )
                self.stderr.write("%s\n" % (msg, ))
                raise command.CommandError(msg)

        return db


class Clean(_DBCommand):

    description = """Clean old views for a database."""

    @defer.inlineCallbacks
    def doLater(self, args):
        db = self.getDB(args, 'clean')

        client = self.parentCommand.parentCommand.getAdminClient()
        d = client.cleanDB(db)
        d.addErrback(common.errback, self)

        yield d

class Compact(_DBCommand):

    description = """Compact a database."""

    @defer.inlineCallbacks
    def doLater(self, args):
        db = self.getDB(args, 'compact')

        client = self.parentCommand.parentCommand.getAdminClient()
        d = client.compactDB(db)
        d.addErrback(common.errback, self)
        yield d


class Create(_DBCommand):

    description = """Create a database."""

    @defer.inlineCallbacks
    def doLater(self, args):
        db = self.getDB(args, 'create')

        client = self.parentCommand.parentCommand.getAdminClient()
        d = client.createDB(db)
        d.addErrback(common.errback, self)
        yield d

class List(tcommand.TwistedCommand):

    description = """List databases."""

    @defer.inlineCallbacks
    def doLater(self, args):
        client = self.parentCommand.parentCommand.getAdminClient()
        gen = yield client.listDB()
        for name in gen:
            self.stdout.write('%s\n' % name)

class Database(logcommand.LogCommand):

    subCommandClasses = [Clean, Compact, Create, List, view.View]

    aliases = ['db', ]

    description = 'Interact with databases.'
