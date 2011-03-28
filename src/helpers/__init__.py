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
"""Helpers for git-hg
"""
import inspect
import os
import subprocess
import sys
import time
import traceback

import pgl

def ensure_is_ghg():
    """Ensure we've calculated a git-hg repository correctly. Raises an
    exception if we haven't, otherwise succeeds silently.
    """
    if not os.path.exists(pgl.config['HG_META']):
        raise Exception, 'This does not appear to be a git-hg repo (HM)'
    if not os.path.exists(pgl.config['HG_REPO']):
        raise Exception, 'This does not appear to be a git-hg repo (HR)'
    if not os.path.exists(pgl.config['HG_GIT_REPO']):
        raise Exception, 'This does not appear to be a git-hg repo (GR)'

def update_remote():
    """Pull changes from the hg source through our private hg repo and into our
    private git remote.
    """
    # Get changes from hg upstream
    hg = subprocess.Popen(['hg', 'pull'], stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, cwd=pgl.config['HG_REPO'], bufsize=1)
    for line in hg.stdout:
        # Don't want to show the "(run 'hg update' to get a working copy)" line
        if not line.startswith('('):
            # Let's not confuse git users with mercurial's terminology
            if line.startswith('pulling'):
                line = line.replace('pulling ', 'fetching ')
            sys.stdout.write('HG: %s' % (line,))
            sys.stdout.flush()

    # Push those changes into our git remote
    sys.stdout.write('Converting hg->git (this may take a while)\n')
    sys.stdout.flush()
    hg2git()

def hg2git():
    """Using hg-git, export a private hg repo into a private git repository.
    Also, do some nice logging so we know what happened.
    """
    debug = file(pgl.config['HG_DEBUG'], 'a')

    debug.write('=' * 70)
    debug.write('\n')
    start = int(time.time())
    debug.write('STARTING HG->GIT EXPORT @ %s\n' % (time.ctime(start).upper(),))
    debug.write('\n')

    # Bookmark all our branches
    branches = subprocess.Popen(['hg', 'branches'], stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, cwd=pgl.config['HG_REPO'], bufsize=1)
    for line in branches.stdout:
        branch, _ = line.strip().split(' ', 1)
        if branch == 'default':
            gbranch = 'master'
        else:
            gbranch = branch
        marker = subprocess.Popen(['hg', 'bookmark', '-f', '-r', branch,
            'hg/%s' % gbranch], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=pgl.config['HG_REPO'], bufsize=1)
        marker.wait()
    branches.wait()

    # Start the exporter, using our provided hg-git
    export_args = ['hg', '--debug', '-v', '--config', 'extensions.hggit=',
                   'gexport']
    exporter = subprocess.Popen(export_args, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, cwd=pgl.config['HG_REPO'], bufsize=1)

    ncommits = None
    for line in exporter.stdout:
        if line.startswith('importing: '):
            bits = line.strip().split()
            if len(bits) > 2:
                cur_commit, ncommits = map(int, bits[1].split('/'))
                cur_commit += 1
                pct = int(float(cur_commit * 100) / float(ncommits))
                sys.stdout.write('\r%s' % (' ' * 70,))
                sys.stdout.write('\rImporting revision %s/%s (%s%%)' %
                    (cur_commit, ncommits, pct))
                sys.stdout.flush()
        debug.write(line)
    sys.stdout.write('\n')
    sys.stdout.flush()

    stat = exporter.wait()
    if stat:
        sys.stderr.write('Some error occurred importing from hg\n')

    end = int(time.time())
    debug.write('FINISHED HG->GIT EXPORT @ %s\n' % (time.ctime(end).upper(),))
    debug.write('ELAPSED TIME: %s SEC\n' % (end - start,))
    debug.write('=' * 70)
    debug.write('\n')
    debug.write('\n')

    debug.close()

def include_hg_setup():
    """Add the git-hg specific portions of our setup into the pgl.config dict.
    """
    pgl.config['HG_META'] = os.path.join(pgl.config['GIT_DIR'], 'hg')
    pgl.config['HG_REPO'] = os.path.join(pgl.config['HG_META'], 'repo')
    pgl.config['HG_GIT_REPO'] = os.path.join(pgl.config['HG_REPO'], '.git')
    pgl.config['HG_DEBUG'] = os.path.join(pgl.config['HG_META'], 'debug.log')
    pgl.config['HG_PYPATH'] = os.path.join(pgl.config['GIT_LIBEXEC'], 'ghg')
