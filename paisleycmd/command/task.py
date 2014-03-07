# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

"""
The tasks command
"""

from twisted.internet import defer

from paisleycmd.extern.command import tcommand

from paisleycmd.common import logcommand


class List(tcommand.TwistedCommand):

    description = """List active tasks."""

    @defer.inlineCallbacks
    def doLater(self, args):
        client = self.getRootCommand().getClient()
        res = yield client.get('/_active_tasks')
        tasks = yield client.parseResult(res)
        for task in tasks:
            self.stdout.write('%s in pid %s:\n' % (
                task['type'], task['pid']))
            p = task.get('progress', None)
            if p:
                self.stdout.write('  %d%% done.\n' % (p, ))

            if task['type'] == 'replication':
                self.stdout.write('  source: %s\n  target: %s\n' % (
                    task['source'], task['target']))
            if task['type'] == 'view_compaction':
                self.stdout.write('  database: %s, design doc: %s\n' % (
                        task['database'], task['design_document']))
            if task['type'] == 'database_compaction':
                self.stdout.write('  database: %s\n' % (
                        task['database'], ))


class Task(logcommand.LogCommand):

    subCommandClasses = [List, ]

    description = 'Interact with tasks.'
