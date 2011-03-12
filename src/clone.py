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
import sys

import ghg

@ghg.main
def main():
    ap = argparse.ArgumentParser(description='Clone an hg repository',
        prog='git hg clone')
    ap.add_argument('url', help='URL of HG repository')
    ap.add_argument('path', nargs='?', help='Destination directory')
    args = ap.parse_args(sys.argv[1:])

    if not args.path:
        args.path = os.path.join(os.getcwd(), os.path.basename(args.url))

    # Figure out the absolute path to our repo
    if not os.path.isabs(args.path):
        args.path = os.path.join(os.getcwd(), args.path)
    args.path = os.path.abspath(args.path)

    # Create our git repo
    os.mkdir(args.path)
    os.chdir(args.path)
    os.system('git init')

    # Create our bare hg repo under the git metadir
    sys.stdout.write('Cloning hg repository\n')
    sys.stdout.flush()
    os.chdir('.git')
    os.mkdir('hg')
    os.chdir('hg')
    os.system('hg clone -U "%s" repo' % (args.url,))
    os.chdir('repo')
    os.system('hg bookmark -r default master')

    # These variables were missing from our config.
    ghg.config['GIT_TOPLEVEL'] = args.path
    ghg.config['GIT_DIR'] = os.path.join(args.path, '.git')
    ghg.include_hg_setup()
    os.system('git init --bare %s' % (ghg.config['HG_GIT_REPO'],))

    # Go back to the root of our git repo and make go on the export
    sys.stdout.write('Exporting hg->git (this may take a while)\n')
    sys.stdout.flush()
    os.chdir(args.path)
    ghg.hg2git()

    # Create hg remote for local repo
    os.chdir(args.path)
    start = len(ghg.config['GIT_TOPLEVEL'])
    if os.path.split(ghg.config['GIT_TOPLEVEL'])[-1]:
        start += 1
    remote_path = ghg.config['HG_GIT_REPO'][start:]
    os.system('git remote add hg %s' % (remote_path,))

    # Get all the info from our private remote
    os.system('git fetch hg')

    # Finally, checkout our master branch
    os.system('git reset --hard hg/master')

    return 0
