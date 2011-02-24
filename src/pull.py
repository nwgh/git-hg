#!/usr/bin/env python

import argparse
import os
import sys
from git_py_setup import config
from git_hg_helpers.hg2git import hg2git

def main():
    ap = argparse.ArgumentParser(description='Pull updates from hg',
        prog='git hg pull')
    args = ap.parse_args(sys.argv[1:])

    metadir = os.path.join(config['GIT_DIR'], 'hg')
    repodir = os.path.join(metadir, 'repo')

    # Do some sanity checks to make sure we're where we think we are
    if not os.path.exists(metadir) or not os.path.exists(repodir):
        sys.stderr.write('This does not appear to be a git-hg repository\n')
        return 1

    # Use our existing fetch program to get the changes into git
    os.system('git hg fetch')

    # TODO - pull is currently the same as fetch. Haven't figured out how to
    # handle the updates of local branches yet
    sys.stdout.write('\n')
    sys.stdout.write('WARNING!\n')
    sys.stdout.write('git hg pull is currently the same as git hg fetch.\n')
    sys.stdout.write('You MUST update your local branches on your own.\n')
    sys.stdout.flush()
    return 0

if __name__ == '__main__':
    rval = 1

    try:
        rval = main()
    except Exception, e:
        sys.stderr.write('%s\n' % (e,))

    sys.exit(rval)
