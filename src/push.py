#!/usr/bin/env python

import argparse
import os
import subprocess
import sys
from git_py_setup import config
from git_hg_helpers.git2hg import git2hg
from git_hg_helpers.hg2git import update_heads

def main():
    ap = argparse.ArgumentParser(description='Push to an hg repository',
        prog='git hg push')
    ap.add_argument('gitbranch', help='Local git branch to push')
    ap.add_argument('hgbranch', nargs='?', help='Remote hg branch to push to')
    args = ap.parse_args(sys.argv[1:])

    if not args.hgbranch:
        args.hgbranch = args.gitbranch

    metadir = os.path.join(config['GIT_DIR'], 'hg')
    repodir = os.path.join(metadir, 'repo')

    # Do some sanity checks to make sure we're where we think we are
    if not os.path.exists(metadir) or not os.path.exists(repodir):
        sys.stderr.write('This does not appear to be a git-hg repository\n')
        return 1

    os.chdir(repodir)
    cmd = 'git rev-parse -q --verify "%s" > /dev/null'
    if os.system(cmd % (args.gitbranch,)) != 0:
        sys.stderr.write('Branch %s does not appear to exist\n' %
            (args.gitbranch,))
        return 1

    ghgbranch = 'hg/%s' % (args.hgbranch,)
    # TODO - put local branch onto git-hg reference branch
    update_heads(config['HG_HEADS'])

    debug = file(config['HG_DEBUG'], 'w+')
    debug.write('=' * 70)
    debug.write('\n')
    debug.write('STARTING GIT->HG EXPORT @ %s\n' % (time.ctime().upper(),))
    debug.write('GIT BRANCH: %s\n' % (args.gitbranch,))
    debug.write('HG BRANCH: %s\n' % (args.hgbranch,))
    debug.write('\n')

    export_args = ['git', 'fast-export',
                   '--export-marks=%s' % config['HG_MARKS'],
                   '--import-marks=%s' % config['HG_MARKS'], ghgbranch]
    import_args = ['hg', '--config',
                   'extensions.fastimport=%s' % (config['HG_FASTIMPORT'],),
                   '-R', config['HG_REPO'], 'fastimport', '-']
    exporter = subprocess.Popen(export_args, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    importer = subprocess.Popen(import_args, stdin=exporter.stdout,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    estat = exporter.wait()
    istat = importer.wait()

    for line in exporter.stderr:
        debug.write('EXPORTER: %s' % (line,))
    for line in importer.stdout:
        debug.write('IMPORTER: %s' % (line,))

    debug.write('=' * 70)
    debug.write('\n')
    debug.write('\n')

    debug.close()

    if estat:
        sys.stderr.write('Some error occurred exporting from git.\n')
        return 1
    elif istat:
        sys.stderr.write('Some error occurred importing to hg.\n')
        return 1

    return 0

if __name__ == '__main__':
    rval = 1

    try:
        rval = main()
    except Exception, e:
        sys.stderr.write('%s\n' % (str(e),))

    sys.exit(rval)
