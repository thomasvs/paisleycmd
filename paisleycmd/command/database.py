# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

"""
The database command
"""

from twisted.internet import defer

from paisleycmd.extern.command import tcommand

from paisleycmd.common import log
from paisleycmd.common import logcommand
from paisleycmd.command import view


class Create(tcommand.TwistedCommand):

    description = """Create a database."""

    @defer.inlineCallbacks
    def doLater(self, args):
        if not args:
            self.stderr.write('Please give database name to create.\n')
            defer.returnValue(3)
            return

        yield self.parentCommand.parentCommand.db.createDB(args[0])


class List(tcommand.TwistedCommand):

    description = """List databases."""

    @defer.inlineCallbacks
    def doLater(self, args):
        gen = yield self.parentCommand.parentCommand.db.listDB()
        for name in gen:
            self.stdout.write('%s\n' % name)

class Database(logcommand.LogCommand):

    subCommandClasses = [Create, List, view.View]

    description = 'Interact with databases.'
