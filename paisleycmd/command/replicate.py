# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import urlparse

from twisted.internet import defer
from twisted.web import error as twerror

from paisley import pjson as json

from paisleycmd.extern.log import log

from paisleycmd.common import logcommand, urlrewrite

HOST = 'localhost'
PORT = 5984


class Add(logcommand.TwistedLogCommand):
    summary = "Add another database to replicate with"
    usage = "http[s]://[USER[:PASSWORD]@]HOST[:PORT][/DB]"
    description = """Set up replication with another database.

If you provide a username, but not a password, you will be prompted for
the remote password.

Example: gtd replicate add http://thomas@otto
will add a two-way replication to the mushin database on the host 'otto',
authenticating as the user 'thomas', and asking for a password.

The default remote host is %s.
The default remote port is %d.
""" % (HOST, PORT)

    def addOptions(self):
        self.parser.add_option('-t', '--type',
            action="store", dest="type",
            help="single/continuous", default="continuous")
        self.parser.add_option('-d', '--direction',
            action="store", dest="direction",
            help="forward/backward/both", default="both")

    @defer.inlineCallbacks
    def doLater(self, args):
        root = self.getRootCommand()
        sourceUri = '/' + root.getDatabase()
        client = self.getRootCommand().getClient()

        # figure out target
        try:
            url = args[0]
        except IndexError:
            self.stdout.write('Please give a database to replicate to.\n')
            return

        # urlparse really needs a scheme there
        if not url.startswith('http'):
            url = 'http://' + url

        # if a username was given, but no password, ask for it
        parsed = urlparse.urlparse(url)
        self.log('url %s parsed to %r', url, parsed)
        password = None
        if parsed.username and not parsed.password:
            password = root.getPassword(
                prompt='\nPassword for target database %s: ' % url)

        # default to same db name on different host
        jane = urlrewrite.rewrite(url, hostname=HOST, port=PORT,
            password=password, path=sourceUri)

        self.log('remote url rewritten to %s', jane)

        # figure out source
        # sourceUri = '/' + root.getDatabase()
        # tarzan = client.url_template % sourceUri
        tarzan = root.getDatabase()

        self.log('local url rewritten to %s', tarzan)

        dbs = []
        if self.options.direction in ['forward', 'both']:
            dbs.append((tarzan, jane))
        if self.options.direction in ['backward', 'both']:
            dbs.append((jane, tarzan))


        for source, target in dbs:
            s = json.dumps({
              "source": source,
              "target": target,
              "continuous": self.options.type == 'continuous'})
            self.info('replicating from %s to %s',
                urlrewrite.rewrite_safe(source),
                urlrewrite.rewrite_safe(target))

            try:
                d = client.post('/_replicate', s)
            except Exception, e:
                self.stdout.write('Exception %r\n' % e)
                self.stdout.write(
                    'FAILED: local server failed for source %s\n' %
                        source.encode('utf-8'))
                self.stdout.write('Is the server running ?\n')
                defer.returnValue(e)
                return

            error = None # set with a non-newline string in case of error

            try:
                result = yield d
            except twerror.Error, e:
                error = 'CouchDB returned error response %r' % e.status
                try:
                    self.debug('CouchDB message: %r', e.message)
                    r = json.loads(e.message)
                    error = 'CouchDB returned error reason: %s' % r['reason']
                except:
                    pass
            except Exception, e:
                error = log.getExceptionMessage(e)

            if not error:
                r = json.loads(result)

                try:
                    if r['ok']:
                        self.stdout.write('+ Replicating %s to %s\n' % (
                            urlrewrite.rewrite_safe(source.encode('utf-8')),
                            urlrewrite.rewrite_safe(target.encode('utf-8'))))
                    else:
                        error = r
                except Exception, e:
                    error = 'Exception: %r\n' % e

            if error:
                self.stdout.write('- Failed to replicate %s to %s:\n' % (
                    urlrewrite.rewrite_safe(source.encode('utf-8')),
                    urlrewrite.rewrite_safe(target.encode('utf-8'))))
                self.stdout.write('  %s\n' % error.encode('utf-8'))

class Replicate(logcommand.LogCommand):
    description = """Manage replication.
"""

    subCommandClasses = [Add, ]
