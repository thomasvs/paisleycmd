# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

from twisted.internet import defer

from paisleycmd.extern.command import command, tcommand

from paisleycmd.common import logcommand, common


class Restart(logcommand.TwistedLogCommand):

    summary = "Restart the viewserver of the given type."

    @defer.inlineCallbacks
    def doLater(self, args):
        if not args:
            self.stderr.write('Please give a view server type to restart.\n')
            defer.returnValue(3)
            return

        self._client = self.getRootCommand().getAdminClient()

        url = '/_config/query_servers/%s' % args[0]
        server = yield self._client.get(url)
        self.debug('server: %s', server)

        # FIXME: isn't it weird that get gives me unicode but put doesn't take
        # it ?
        yield self._client.put(url, server.encode('utf-8'))



class ViewServer(logcommand.LogCommand):

    subCommandClasses = [Restart]

    description = 'Interact with view servers.'
