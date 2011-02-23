#!/usr/bin/env python

import sys

def die(msg):
    sys.stderr.write('%s\n')
    sys.exit(1)

if sys.version_info.major == 2:
    if sys.version_info.minor < 7:
        die('Python 2 must be version 2.7 or higher')
elif sys.version_info.major == 3:
    if sys.version_info.minor < 2:
        die('Python 3 must be version 3.2 or higher')
else:
    die('Python must be version 2.7 or 3.2 or higher')

try:
    import mercurial
except ImportError, e:
    die('You must have the mercurial library installed')

# If we get to the end of the script, all our checks have passed, so we can
# continue on!
sys.exit(0)
