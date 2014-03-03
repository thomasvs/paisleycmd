# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

'''
configure-time variables for installed or uninstalled operation

Code should run
    >>> from paisleycmd.configure import configure

and then access the variables from the configure module.  For example:
    >>> print configure.version

@var  isinstalled: whether an installed version is being run
@type isinstalled: boolean

@var  version:     paisleycmd version number
@type version:     string
'''

import os

# where am I on the disk ?
__thisdir = os.path.dirname(os.path.abspath(__file__))

if os.path.exists(os.path.join(__thisdir, 'uninstalled.py')):
    from paisleycmd.configure import uninstalled
    config_dict = uninstalled.get()
elif os.path.exists(os.path.join(__thisdir, 'installed.py')):
    from paisleycmd.configure import installed
    config_dict = installed.get()
else:
    # hack on fresh checkout, no make run yet, and configure needs revision
    from paisleycmd.common import common
    config_dict = {
        'revision': common.getRevision(),
    }

for key, value in config_dict.items():
    dictionary = locals()
    dictionary[key] = value
