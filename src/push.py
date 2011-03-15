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

import argparse
import os
import subprocess
import sys
import time

import ghg

@ghg.main
def main():
    ap = argparse.ArgumentParser(description='Push to an hg repository',
        prog='git hg push')
    ap.add_argument('gitbranch', help='Local git branch to push')
    ap.add_argument('hgbranch', nargs='?', help='Remote hg branch to push to')
    args = ap.parse_args(sys.argv[1:])

    if not args.hgbranch:
        args.hgbranch = args.gitbranch

    # Do some sanity checks to make sure we're where we think we are
    ghg.ensure_is_ghg()

    # Make sure we'll error if things have changed somewhere else
    ghg.update_remote()

    debug = file(ghg.config['HG_DEBUG'], 'a')
    debug.write('=' * 70)
    debug.write('\n')
    start = int(time.time())
    debug.write('STARTING GIT->HG EXPORT @ %s\n' % (time.ctime(start).upper(),))
    debug.write('GIT BRANCH: %s\n' % (args.gitbranch,))
    debug.write('HG BRANCH: %s\n' % (args.hgbranch,))
    debug.write('\n')

    cmd = 'git push hg %s:hg/%s' % (args.gitbranch, args.hgbranch)
    debug.write('=> %s\n' % cmd)
    os.system(cmd)
    debug.write('\n')

    import_args = ['hg', '--debug', '-v', '--config', 'extensions.hggit=',
                   'gimport']
    debug.write('=> %s\n' % ' '.join(import_args))
    importer = subprocess.Popen(import_args, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, cwd=ghg.config['HG_REPO'])

    for line in importer.stdout:
        if line.startswith('importing: '):
            bits = line.strip().split()
            if len(bits) > 2:
                sys.stdout.write('\r%s' % (' ' * 70,))
                sys.stdout.write('\rExporting revision %s %s' %
                    (bits[1], bits[3]))
                sys.stdout.flush()
        debug.write(line)
    sys.stdout.write('\n')
    sys.stdout.flush()
    debug.write('\n')

    rval = importer.wait()
    if rval:
        sys.stderr.write('Some error occurred exporting to hg\n')
    else:
        oldcwd = os.getcwd()
        os.chdir(ghg.config['HG_REPO'])
        rval = os.system('hg push')
        os.chdir(oldcwd)

    end = int(time.time())
    debug.write('FINISHED HG->GIT EXPORT @ %s\n' % (time.ctime(end).upper(),))
    debug.write('ELAPSED TIME: %s SEC\n' % (end - start,))
    debug.write('=' * 70)
    debug.write('\n')
    debug.write('\n')

    debug.close()

    return rval
