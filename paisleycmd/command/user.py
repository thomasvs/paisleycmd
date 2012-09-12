# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

"""
The user command
"""

import os
import hashlib

from twisted.internet import defer
from twisted.web import error, http

from paisleycmd.extern.paisley import pjson as json

from paisleycmd.common import logcommand
from paisleycmd.common import log

def handleCouchException(cmd, e):
    try:
        message = json.loads(e.message)
        cmd.stderr.write("CouchDB error: %s\n" % message['reason'])
        return 3
    except:
        raise


class Add(logcommand.TwistedLogCommand):

    description = """Add user"""


    def addOptions(self):
        self.parser.add_option('-r', '--role',
                          action="append", dest="roles",
                          help="role", default=[])


    @defer.inlineCallbacks
    def doLater(self, args):
        if not args:
            self.stderr.write('Please specify the name of the user to add.\n')
            defer.returnValue(3)
            return

        user = args[0]

        h = hashlib.sha1()

        password = self.getRootCommand().getPassword()
        h.update(password)
        del password

        salt = os.urandom(16).encode('hex')
        h.update(salt)

        password_sha = h.hexdigest()

        roles = self.options.roles

        docId = "org.couchdb.user:" + user

        doc = {
            "_id": docId,
            "type": "user",
            "name": user,
            "roles": roles,
            "password_sha": password_sha,
            "salt": salt
        }

        self.debug('Saving doc %r', doc)
        try:
            d = self.parentCommand.getAdminClient().saveDoc('_users',
                doc, docId)
        except Exception, e:
            self.warning('saveDoc triggered exception: %s',
                log.getExceptionMessage(e))
            raise

        try:
            result = yield d
        except error.Error, e:
            if e.status == http.CONFLICT:
                self.stderr.write("Error: the user '%s' already exists.\n" %
                    user)
                defer.returnValue(3)
                return

            ret = handleCouchException(self, e)
            if ret:
                defer.returnValue(ret)
                return
        except Exception, e:
            self.warning('yielding saveDoc triggered exception: %s',
                log.getExceptionMessage(e))
            raise

        if result['ok']:
            self.stdout.write("Added user '%s'.\n" % user)
        else:
            self.stdout.write("Unknown error.  Result: %r\n" % result)


class Delete(logcommand.TwistedLogCommand):

    usage = """USER [.. USER]"""
    description = """Delete given user(s)"""


    @defer.inlineCallbacks
    def doLater(self, args):
        if not args:
            self.stderr.write(
                'Please specify the name of the user(s) to delete.\n')
            defer.returnValue(3)
            return

        client = self.parentCommand.getAdminClient()

        failures = 0

        for user in args:

            self.debug('Deleting user %r', user)
            docId = "org.couchdb.user:" + user

            try:
                result = yield client.openDoc('_users', docId)
            except error.Error, e:
                if e.status == http.NOT_FOUND:
                    self.stderr.write("Could not find user '%s'\n" % user)
                    failures += 1
                    continue
                raise
            except Exception, e:
                raise

            self.debug('Deleting docId %s at revision %s', docId, result['_rev'])
            try:
                d = client.deleteDoc('_users', docId,
                    result['_rev'])
            except Exception, e:
                self.warning('deleteDoc triggered exception: %s',
                    log.getExceptionMessage(e))
                self.stderr.write("Could not delete user '%s'\n" % user)
                failures += 1
                continue

            try:
                result = yield d
            except error.Error, e:
                self.stderr.write("Error: %s\n" % e.reason)
                failures += 1
                continue
            except Exception, e:
                self.warning('yielding deleteDoc triggered exception: %s',
                    log.getExceptionMessage(e))
                failures += 1
                continue

            if result['ok']:
                self.stdout.write("Deleted user '%s'.\n" % user)
            else:
                self.stdout.write("Unknown error.  Result: %r\n" % result)
                failures += 1


class List(logcommand.TwistedLogCommand):

    description = """List users."""

    @defer.inlineCallbacks
    def doLater(self, args):
        result = yield self.getRootCommand().db.listDoc('_users',
            include_docs=True)


        for row in result['rows']:
            if not row['id'].startswith('org.couchdb.user:'):
                continue
            self.stdout.write(row['doc']['name'] + '\n')

class User(logcommand.LogCommand):

    subCommandClasses = [Add, Delete, List]

    description = 'Interact with the _users database'

    def addOptions(self):
        self.parser.add_option('-A', '--admin-user',
                          action="store", dest="admin",
                          help="Admin username", default="")

    def getAdminClient(self):
        client = self.getRootCommand().getClient()
        if self.options.admin:
            password = self.getRootCommand().getPassword(
                'Password for %s:' % self.options.admin)
            client.username = self.options.admin
            client.password = password

        return client
