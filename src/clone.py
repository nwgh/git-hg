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
if sys.version_info.major == 2:
    import ConfigParser as cp
else:
    import configparser as cp

import ghg
import pgl

@pgl.main
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

    # Configure hg-git to put our .git directory alongside our .hg directory
    os.chdir('repo')
    os.chdir('.hg')
    conf = cp.RawConfigParser()
    conf.read('hgrc')
    conf.add_section('git')
    conf.set('git', 'intree', 'True')
    with file('hgrc', 'w') as f:
        conf.write(f)

    # These variables were missing from our config.
    pgl.config['GIT_TOPLEVEL'] = args.path
    pgl.config['GIT_DIR'] = os.path.join(args.path, '.git')
    ghg.include_hg_setup()

    # Go back to the root of our git repo and make go on the export
    sys.stdout.write('Converting hg->git (this may take a while)\n')
    sys.stdout.flush()
    os.chdir(args.path)
    ghg.hg2git()

    # Create hg remote for local repo
    os.chdir(args.path)
    start = len(pgl.config['GIT_TOPLEVEL'])
    if os.path.split(pgl.config['GIT_TOPLEVEL'])[-1]:
        start += 1
    remote_path = pgl.config['HG_GIT_REPO'][start:]
    os.system('git config remote.hg.url %s' % (remote_path,))
    os.system('git config remote.hg.fetch +refs/heads/hg/*:refs/remotes/hg/*')

    # Set up our master branch to track hg's default
    os.system('git config branch.master.remote hg')
    os.system('git config branch.master.merge refs/heads/hg/master')
    if pgl.config.get('branch.autosetuprebase', None) in ('remote', 'always'):
        os.system('git config branch.master.rebase true')

    # Get all the info from our private remote
    os.system('git fetch hg')

    # Finally, checkout our master branch
    os.system('git reset --hard hg/master')

    return 0
