# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

"""
The document command
"""

import subprocess

from twisted.internet import defer

from paisleycmd.extern.paisley import client

from paisleycmd.extern.command import command, tcommand

from paisleycmd.common import logcommand

class _ScriptCommand(tcommand.TwistedCommand):

    def addOptions(self):
        self.parser.add_option('-d', '--dry-run',
                          action="store_true", dest="dryrun",
                          help="show documents that would be changed, "
                            "without changing them")


    @defer.inlineCallbacks
    def doScript(self, args):
        self.rows = 0

        if not args:
            self.stderr.write('Please give script to apply.\n')
            defer.returnValue(3)
            return

        self.process = subprocess.Popen(
            args, env=None, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)


        db = self.getRootCommand().getClient()
        allDocs = yield db.listDoc(
            self.getRootCommand().getDatabase(), include_docs=True)

        for row in allDocs['rows']:
            self.rows += 1
            doc = row['doc']
            self.debug('passing doc %r', doc)
            try:
                self.process.stdin.write(client.json.dumps(doc) + '\n')
            except IOError:
                # error 32, Broken Pipe, can happen if the script fails
                # FIXME: not sure if that is the only error possible and
                # if there will always be stderr output
                raise command.CommandError('Error running script: '
                    + self.process.stderr.read())
            result = self.process.stdout.readline().rstrip()
            yield self.handledRow(row, result)

        self.process.terminate()
        self.process.wait()

    def handledRow(self, row, result):
        """
        @type  result: str

        @rtype: L{defer.Deferred}
        """
        raise NotImplementedError

class Apply(_ScriptCommand):

    usage = """APPLY_SCRIPT"""
    summary = "apply a transformation to all documents"

    description = """
Apply a transformation to all documents.

The script will receive each document, JSON-encoded, on a single line.
The script should output an empty line for each input line if it doesn't
want to transform the document, or the transformed version of the document
if it does.
"""

    @defer.inlineCallbacks
    def doLater(self, args):
        self._updated = 0

        yield self.doScript(args)

        self.stdout.write('%d of %d documents changed.\n' % (
            self._updated, self.rows))

    @defer.inlineCallbacks
    def handledRow(self, row, result):
        db = self.getRootCommand().getClient()

        if result:
            self._updated += 1
            if self.options.dryrun:
                self.stdout.write("%s\n" % result.encode('utf-8'))
            else:
                doc = client.json.loads(result)

                if row['key'] == doc['_id']:
                    # no _id change
                    yield db.saveDoc(
                        self.getRootCommand().getDatabase(),
                        result, doc['_id'])
                else:
                    # _id change, so save the doc under new id and delete old
                    del doc['_rev']
                    try:
                        yield db.saveDoc(
                            self.getRootCommand().getDatabase(),
                            client.json.dumps(doc), doc['_id'])
                    except:
                        pass
                    yield db.deleteDoc(
                        self.getRootCommand().getDatabase(),
                        row['key'], row['doc']['_rev'])


class Delete(_ScriptCommand):

    usage = """DELETE_SCRIPT"""
    summary = "Delete documents selected by the delete script"

    description = """
Delete documents selected by the delete script.

The script will receive each document, JSON-encoded, on a single line.

The script should output an empty line for each input line if it doesn't
want to delete the document, or the word 'DELETE' if it does.
"""
    def addOptions(self):
        _ScriptCommand.addOptions(self)
        self.parser.add_option('-v', '--verbose',
                          action="store_true", dest="verbose",
                          help="show full documents")


    @defer.inlineCallbacks
    def doLater(self, args):
        self._deleted = 0

        yield self.doScript(args)

        self.stdout.write('%d of %d documents deleted.\n' % (
            self._deleted, self.rows))

    @defer.inlineCallbacks
    def handledRow(self, row, result):

        db = self.getRootCommand().getClient()
        if result == 'DELETE':
            self._deleted += 1
            if self.options.dryrun:
                if self.options.verbose:
                    self.stdout.write('Deleting doc %r\n' % row['doc'])
                else:
                    self.stdout.write('Deleting id %r\n' % row['key'])
            else:
                ret = yield db.deleteDoc(
                    self.getRootCommand().getDatabase(),
                    row['key'], row['doc']['_rev'])


class Document(logcommand.LogCommand):

    subCommandClasses = [Apply, Delete]
    aliases = ['doc', ]

    description = 'Interact with documents'
