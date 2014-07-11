# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

"""
The main entry point for the 'paisley' command-line application.
"""

import sys
import optparse
import warnings

from paisleycmd.extern.command import command
from paisleycmd.extern.command import tcommand

from paisleycmd.extern.paisley import client

from paisleycmd.common import log
from paisleycmd.common import logcommand
from paisleycmd.command import database, document, replicate, security, task
from paisleycmd.command import user, viewserver
from paisleycmd.configure import configure

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
        optparse.Option('-S', '--ssl',
            action="store_true", dest="ssl",
            help="Use SSL for connection",
            default=None),
]


def main(argv):

    if not configure.isinstalled:
        # good boy, you deserve to help us fix warnings
        warnings.simplefilter('default')

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


class Paisley(tcommand.ReactorCommand, logcommand.LogCommand):
    usage = "%prog %command"
    description = """paisley is a CouchDB client.

paisley gives you a tree of subcommands to work with.
You can get help on subcommands by using the -h option to the subcommand.
"""

    subCommandClasses = [
        database.Database,
        document.Document,
        replicate.Replicate,
        security.Security,
        task.Task,
        user.User,
        viewserver.ViewServer,
    ]

    db = None

    def addOptions(self):
        self.parser.add_options(couchdb_option_list)
        # FIXME: is this the right place ?
        log.init()
        from paisleycmd.configure import configure
        log.debug("paisley", "This is paisley version %s (%s)",
            configure.version, configure.revision)
        log.logTwisted()
        log.adaptStandardLogging('paisley', 'paisley', 'paisley')

        self.parser.add_option('-v', '--version',
                          action="store_true", dest="version",
                          help="show version information")

        self.parser.add_option('-u', '--username',
                          action="store", dest="username",
                          help="username", default="")
        self.parser.add_option('-p', '--password',
                          action="store", dest="password",
                          help="password", default=None)
        self.parser.add_option('-f', '--password-file',
                          action="store", dest="password_file",
                          help="password file", default="")



    def handleOptions(self, options):
        if options.version:
            from paisley.configure import configure
            print "paisley %s" % configure.version
            sys.exit(0)

        self.db = self.getClient()

    def getClient(self):
        protocol = 'http'
        if self.options.ssl:
            protocol = 'https'

        c = client.CouchDB(self.options.host, int(self.options.port),
            protocol=protocol)

        password = None

        # if -P without specified password, prompt for it
        if self.options.password == "":
            password = self.getPassword(
                'Password for user %s:' % self.options.username)

        # if -P with specified, use it
        if self.options.password:
            password = self.options.password

        # if we have a password file, use it
        if not password:
            if self.options.password_file:
                try:
                    with open(self.options.password_file, "r") as handle:
                        password = handle.read().strip()
                except:
                    self.stderr.write(
                        "ERROR: Could not read password from file %s\n" % (
                            self.options.password_file, ))

        if self.options.username:
            c.username = self.options.username
        if password:
            c.password = password

        return c

    def getAdminClient(self):
        warnings.warn("getAdminClient is deprecated in favor of getClient",
            DeprecationWarning, stacklevel=2)

        return self.getClient()



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

