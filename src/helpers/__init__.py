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

config = {}

def ensure_is_ghg():
    """Ensure we've calculated a git-hg repository correctly. Raises an
    exception if we haven't, otherwise succeeds silently.
    """
    if not os.path.exists(config['HG_META']):
        raise Exception, 'This does not appear to be a git-hg repo (HM)'
    if not os.path.exists(config['HG_REPO']):
        raise Exception, 'This does not appear to be a git-hg repo (HR)'
    if not os.path.exists(config['HG_GIT_REPO']):
        raise Exception, 'This does not appear to be a git-hg repo (GR)'

def update_remote():
    """Pull changes from the hg source through our private hg repo and into our
    private git remote.
    """
    # Get changes from hg upstream
    os.chdir(config['HG_REPO'])
    os.system('hg pull')

    # Push those changes into our git remote
    os.chdir(config['GIT_TOPLEVEL'])
    hg2git()

def hg2git():
    """Using hg-git, export a private hg repo into a private git repository.
    Also, do some nice logging so we know what happened.
    """
    debug = file(config['HG_DEBUG'], 'a')

    debug.write('=' * 70)
    debug.write('\n')
    start = int(time.time())
    debug.write('STARTING HG->GIT EXPORT @ %s\n' % (time.ctime(start).upper(),))
    debug.write('\n')

    # Bookmark all our branches
    branches = subprocess.Popen(['hg', 'branches'], stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, cwd=config['HG_REPO'])
    for line in branches.stdout:
        branch, _ = line.strip().split(' ', 1)
        if branch == 'default':
            gbranch = 'master'
        else:
            gbranch = branch
        marker = subprocess.Popen(['hg', 'bookmark', '-f', '-r', branch,
            'hg/%s' % gbranch], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=config['HG_REPO'])
        marker.wait()
    branches.wait()

    # Start the exporter, using our provided hg-git
    export_args = ['hg', '--debug', '-v', '--config', 'extensions.hggit=',
                   'gexport']
    exporter = subprocess.Popen(export_args, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, cwd=config['HG_REPO'])

    for line in exporter.stdout:
        if line.startswith('importing: '):
            bits = line.strip().split()
            if len(bits) > 2:
                sys.stdout.write('\r%s' % (' ' * 70,))
                sys.stdout.write('\rImporting revision %s %s' %
                    (bits[1], bits[2]))
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
    """Add the git-hg specific portions of our setup into the config dict.
    """
    config['HG_META'] = os.path.join(config['GIT_DIR'], 'hg')
    config['HG_REPO'] = os.path.join(config['HG_META'], 'repo')
    config['HG_GIT_REPO'] = os.path.join(config['HG_REPO'], '.git')
    config['HG_DEBUG'] = os.path.join(config['HG_META'], 'debug.log')
    config['HG_PYPATH'] = os.path.join(config['GIT_LIBEXEC'], 'ghg')

def __extract_name_email(info, type_):
    """Extract a name and email from a string in the form:
           User Name <user@example.com>
       Stick that into our config dict for either git committer or git author.
    """
    val = ' '.join(info.split(' ')[:-2])
    angle = val.find('<')
    if angle > -1:
        config['GIT_%s_NAME' % type_] = val[:angle - 1]
        config['GIT_%s_EMAIL' % type_] = val[angle + 1:-1]
    else:
        config['GIT_%s_NAME' % type_] = val

def __create_config():
    """Create our configuration dict from the env variables we're given.
    """
    for k, v in os.environ.iteritems():
        if k == 'PY_GIT_CONFIG':
            cfgs = v.split('\n')
            for cfg in cfgs:
                var, val = cfg.split('=', 1)
                if val == 'true':
                    val = True
                elif val == 'false':
                    val = False
                else:
                    try:
                        val = int(val)
                    except:
                        pass
                config[var] = val
        elif k == 'PY_GIT_COMMITTER_IDENT':
            __extract_name_email(v, 'COMMITTER')
        elif k == 'PY_GIT_AUTHOR_IDENT':
            __extract_name_email(v, 'AUTHOR')
        elif k.startswith('PY_GIT_'):
            config[k[3:]] = v

    if 'GIT_DIR' in config and not os.path.isabs(config['GIT_DIR']):
        git_dir = os.path.join(config['GIT_TOPLEVEL'], config['GIT_DIR'])
        config['GIT_DIR'] = os.path.abspath(git_dir)
    if 'GIT_DIR' in config:
        include_hg_setup()

def main(_main):
    """Mark a function as the main function for our git-hg subprogram. Based
    very heavily on automain by Gerald Kaszuba, but with modifications to make
    it work better for git-hg's purposes.
    """
    parent = inspect.stack()[1][0]
    name = parent.f_locals.get('__name__', None)
    if name == '__main__':
        __create_config()
        rval = 1
        try:
            rval = _main()
        except Exception, e:
            sys.stdout.write('%s\n' % str(e))
            f = file('ghg.tb', 'w')
            traceback.print_tb(sys.exc_info()[2], None, f)
            f.close()
        sys.exit(rval)
    return _main
