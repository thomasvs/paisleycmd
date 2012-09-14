# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

"""
The security command
"""

from twisted.internet import defer
from twisted.web import error, http

from paisleycmd.extern.paisley import pjson as json

from paisleycmd.common import logcommand
from paisleycmd.common import log

class SecurityCommand(logcommand.TwistedLogCommand):

    @defer.inlineCallbacks
    def getSecurity(self):
        self.client = self.getRootCommand().getAdminClient()
        self.db = self.getRootCommand().getDatabase()

        try:
            result = yield self.client.openDoc(self.db, '_security')
        except error.Error, e:
            raise
        except Exception, e:
            raise

        defer.returnValue(result)

class Add(SecurityCommand):

    description = """Add admin or reader to security object"""

    def addOptions(self):
        self.parser.add_option('-p', '--permission',
                          action="store", dest="permission",
                          help="admin or reader (defaults to %default)", 
                          default="reader")
        self.parser.add_option('-t', '--type',
                          action="store", dest="type",
                          help="name or role (defaults to %default)", 
                          default="name")

    @defer.inlineCallbacks
    def doLater(self, args):

        security = yield self.getSecurity()

        # fill in all missing bits
        for p in ['admins', 'readers']:
            if not p in security:
                security[p] = {}
            for t in ['names', 'roles']:
                if not t in security[p]:
                    security[p][t] = []

        self.debug('Adding %s(s) %r to permission %s',
            self.options.type, args, self.options.permission)
        p = self.options.permission + 's'
        t = self.options.type + 's'
        if not p in security:
            security[p] = {}
        if not t in security[p]:
            security[p][t] = []

        security[p][t].extend(args)

        # make sure we only have each item listed once
        security[p][t] = list(set(security[p][t]))

        result = yield self.client.saveDoc(self.db, security, '_security')

        if result['ok']:
            self.stdout.write("Security object changed.\n")
        else:
            self.stdout.write("Unknown error.  Result: %r\n" % result)

class List(SecurityCommand):

    description = """List contents of _security document for a database"""

    @defer.inlineCallbacks
    def doLater(self, args):

        result = yield self.getSecurity()

        for key, value in result.items():
            names = value['names']
            roles = value['roles']
            if names or roles:
                self.stdout.write('%s: \n' % key)
                if names:
                    self.stdout.write('  names: %s\n' % (", ".join(names), ))
                if roles:
                    self.stdout.write('  roles: %s\n' % (", ".join(roles), ))

class Security(logcommand.LogCommand):

    subCommandClasses = [Add, List]

    description = 'Interact with a database\'s  _security document'
