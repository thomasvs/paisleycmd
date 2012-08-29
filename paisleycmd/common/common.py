# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

from paisleycmd.extern.paisley import pjson as json

def errback(failure, cmd):
    from twisted.web import error
    failure.trap(error.Error)

    cmd.stderr.write('ERROR: CouchDB returned an error with code %s\n' %
        failure.value.status)

    try:
        body = json.loads(failure.value.message)
        for key, value in body.items():
            cmd.stderr.write('    - %s: %s\n' % (key, value))
        return
    except:
        pass

    # from twisted.web import http
    # if failure.value.status == http.NOT_FOUND:

    return failure


