# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

"""
The main entry point for the 'paisley' command-line application.
"""

import sys
import optparse
import subprocess

from twisted.internet import defer

from paisleycmd.extern.command import command
from paisleycmd.extern.command import tcommand

from paisleycmd.extern.paisley import client

from paisleycmd.common import log
from paisleycmd.common import logcommand
from paisleycmd.command import database, user, security

_DEFAULT_HOST = 'localhost'
_DEFAULT_PORT = 5984

couchdb_option_list = [
        optparse.Option('-H', '--host',
            action="store", dest="host",
            help="CouchDB hostname (defaults to %default)",
            default=_DEFAULT_HOST),
        optparse.Option('-P', '--port',
            action="store", dest="port", type="int",
            help="CouchDB port (defaults to %default)",
            default=_DEFAULT_PORT),
        optparse.Option('-D', '--database',
            action="store", dest="database",
            help="CouchDB database name",
            default=None),
]


def main(argv):

    c = Paisley()

    try:
        ret = c.parse(argv)
    except SystemError, e:
        sys.stderr.write('paisley: error: %s\n' % e.args)
        return 255
    except ImportError, e:
        # FIXME: decide how to handle
        raise
        # deps.handleImportError(e)
    except command.CommandError, e:
        sys.stderr.write('paisley: error: %s\n' % e.output)
        return e.status

    if ret is None:
        return 0

    return ret


class Apply(tcommand.TwistedCommand):

    usage = """APPLY_SCRIPT"""
    description = """
Apply a transformation to all documents.

The script will receive each document, JSON-encoded, on a single line.
The script should output an empty line for each input line if it doesn't
want to transform the document, or the transformed version of the document
if it does.
"""

    def addOptions(self):
        self.parser.add_option('-d', '--dry-run',
                          action="store_true", dest="dryrun",
                          help="show documents that would be changed, "
                            "without changing them")


    @defer.inlineCallbacks
    def doLater(self, args):
        if not args:
            self.stderr.write('Please give command to apply.\n')
            defer.returnValue(3)
            return

        if not self.parentCommand.options.database:
            self.stderr.write(
                'Please specify a database to apply commands on.\n')
            defer.returnValue(3)
            return

        self.process = subprocess.Popen(
            args, env=None, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)


        result = yield self.parentCommand.db.listDoc(
            self.parentCommand.options.database, include_docs=True)

        rows = 0
        updated = 0

        for row in result['rows']:
            rows += 1
            doc = row['doc']
            self.debug('passing doc %r', doc)
            self.process.stdin.write(client.json.dumps(doc) + '\n')
            #print self.process.stderr.read()
            result = self.process.stdout.readline().rstrip()
            if result:
                updated += 1
                if self.options.dryrun:
                    self.stdout.write("%s\n" % result.encode('utf-8'))
                else:
                    ret = yield self.parentCommand.db.saveDoc(
                        self.parentCommand.options.database,
                        result, row['key'])
        self.process.terminate()
        self.process.wait()

        self.stdout.write('%d of %d documents changed.\n' % (
            updated, rows))


class Paisley(tcommand.ReactorCommand, logcommand.LogCommand):
    usage = "%prog %command"
    description = """paisley is a CouchDB client.

paisley gives you a tree of subcommands to work with.
You can get help on subcommands by using the -h option to the subcommand.
"""

    subCommandClasses = [Apply, database.Database, security.Security,
        user.User, ]

    db = None

    def addOptions(self):
        self.parser.add_options(couchdb_option_list)
        # FIXME: is this the right place ?
        log.init()
        # from dad.configure import configure
        log.debug("paisley", "This is paisley version %s (%s)", "0.0.0", "0")
        #    configure.version, configure.revision)

        self.parser.add_option('-v', '--version',
                          action="store_true", dest="version",
                          help="show version information")

        self.parser.add_option('-A', '--admin-user',
                          action="store", dest="admin",
                          help="Admin username", default="")

    def handleOptions(self, options):
        if options.version:
            from paisley.configure import configure
            print "paisley %s" % configure.version
            sys.exit(0)

        self.db = self.getClient()

    def getClient(self):
        return client.CouchDB(self.options.host, int(self.options.port))

    def getAdminClient(self):
        client = self.getClient()
        if self.options.admin:
            password = self.getPassword(
                'Password for %s:' % self.options.admin)
            client.username = self.options.admin
            client.password = password

        return client

    def getDatabase(self):
        if not self.options.database:
            raise KeyError(
                '%s: Please specify a database with -D as an option' %
                    self.getFullName())
        return self.options.database

    def getPassword(self, prompt='Password: '):
        import getpass
        p = getpass.getpass(prompt)
        self.stdout.write('\n')
        return p

