# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

"""
The main entry point for the 'paisley' command-line application.
"""

import sys
import optparse

from paisleycmd.extern.command import command

from paisleycmd.extern.paisley import client

from paisleycmd.common import log
from paisleycmd.common import logcommand
from paisleycmd.command import database

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

class Paisley(logcommand.LogCommand):
    usage = "%prog %command"
    description = """paisley is a CouchDB client.

paisley gives you a tree of subcommands to work with.
You can get help on subcommands by using the -h option to the subcommand.
"""

    subCommandClasses = [database.Database, ]

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

    def handleOptions(self, options):
        if options.version:
            from paisley.configure import configure
            print "paisley %s" % configure.version
            sys.exit(0)

        self.db = client.CouchDB(options.host, int(options.port))

    def parse(self, argv):
        log.debug("paisley", "paisley %s" % " ".join(argv))
        logcommand.LogCommand.parse(self, argv)

    def getDatabase(self):
        if not self.options.database:
            raise KeyError('Please specify a database with -D')
        return self.options.database

