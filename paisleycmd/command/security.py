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


class List(logcommand.TwistedLogCommand):

    description = """List contents of _security document for a database"""


    @defer.inlineCallbacks
    def doLater(self, args):
        client = self.getRootCommand().getAdminClient()
        db = self.getRootCommand().getDatabase()

        try:
            result = yield client.openDoc(db, '_security')
        except error.Error, e:
            raise
        except Exception, e:
            raise

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

    subCommandClasses = [List]

    description = 'Interact with a database\'s  _security document'


