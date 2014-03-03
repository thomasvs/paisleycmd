# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import os
import commands

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


def getRevision():
    """
    Get a revision tag for the current git source tree.

    Appends -modified in case there are local modifications.

    If this is not a git tree, return the top-level REVISION contents instead.

    Finally, return unknown.
    """
    topsrcdir = os.path.join(os.path.dirname(__file__), '..', '..')

    # only use git if our src directory looks like a git checkout
    # if you run git regardless, it recurses up until it finds a .git,
    # which may be higher than your current source tree
    if os.path.exists(os.path.join(topsrcdir, '.git')):

        status, describe = commands.getstatusoutput('git describe')
        if status == 0:
            if commands.getoutput('git diff-index --name-only HEAD --'):
                describe += '-modified'

            return describe

    # check for a top-level REIVISION file
    path = os.path.join(topsrcdir, 'REVISION')
    if os.path.exists(path):
        revision = open(path).read().strip()
        return revision

    return '(unknown)'
