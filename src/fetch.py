#!/usr/bin/env python

import argparse
import os
import sys
from git_py_setup import config
from git_hg_helpers.hg2git import hg2git

def main():
    ap = argparse.ArgumentParser(description='Fetch updates from hg',
        prog='git hg fetch')
    args = ap.parse_args(sys.argv[1:])

    metadir = os.path.join(config['GIT_DIR'], 'hg')
    repodir = os.path.join(metadir, 'repo')

    # Do some sanity checks to make sure we're where we think we are
    if not os.path.exists(metadir) or not os.path.exists(repodir):
        sys.stderr.write('This does not appear to be a git-hg repository\n')
        return 1

    # Get changes from hg upstream
    os.chdir(repodir)
    os.system('hg pull')

    # Pull those changes into our git repo
    os.chdir(config['GIT_TOPLEVEL'])
    hg2git(config)

    # We don't update any local branches since this is just fetch
    return 0

if __name__ == '__main__':
    rval = 1

    try:
        rval = main()
    except Exception, e:
        sys.stderr.write('%s\n' % (e,))

    sys.exit(rval)
