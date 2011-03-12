#!/usr/bin/env python
#
# Copyright (c) 2011 Nick Hurley <hurley at todesschaf dot org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of version 2 of the GNU General Public License as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

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
    import hggit
except ImportError, e:
    die('You must have hg-git installed')

try:
    import dulwich
except ImportError, e:
    die('You must have dulwich installed')

# If we get to the end of the script, all our checks have passed, so we can
# continue on!
sys.exit(0)
