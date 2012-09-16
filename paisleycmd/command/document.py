# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

"""
The document command
"""

import base64

from twisted.internet import defer

from paisleycmd.extern.command import tcommand

from paisleycmd.common import logcommand

class Apply(tcommand.TwistedCommand):

    usage = """APPLY_SCRIPT"""
    summary = "apply a transformation to all documents"

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


class Document(logcommand.LogCommand):

    subCommandClasses = [Apply]
    aliases = ['doc', ]

    description = 'Interact with documents'
