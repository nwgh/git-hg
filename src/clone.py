#!/usr/bin/env python
import argparse
import os
import sys
from git_py_setup import config
from git_hg_helpers.hg2git import hg2git

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

    # These variables were missing from our config.
    config['GIT_TOPLEVEL'] = args.path
    config['GIT_DIR'] = os.path.join(args.path, '.git')

    # Go back to the root of our git repo and make go on the export
    sys.stdout.write('Exporting hg->git (this may take a while)\n')
    sys.stdout.flush()
    os.chdir(args.path)
    hg2git(config)

    return 0

if __name__ == '__main__':
    rval = 1

    try:
        rval = main()
    except Exception, e:
        sys.stderr.write('%s\n' % (str(e),))

    sys.exit(rval)
