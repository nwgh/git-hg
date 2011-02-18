import os
import sys
from git_py_setup import config
from git_hg_helpers.hg2git import hg2git

def usage():
    raise Exception, 'git hg clone <repository> [<directory>]'

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        usage()

    url = sys.argv[1]
    if len(sys.argv) == 2:
        path = os.path.join(os.getcwd(), os.path.basename(url))
    else:
        path = sys.argv[3]

    # Figure out the absolute path to our repo
    if not os.path.isabs(path):
        path = os.path.join(os.getcwd(), path)
    path = os.path.abspath(path)

    # Create our git repo
    os.mkdir(path)
    os.chdir(path)
    os.system('git init')

    # Create our bare hg repo under the git metadir
    os.chdir('.git')
    os.mkdir('hg')
    os.chdir('hg')
    os.system('hg clone -U "%s" repo' % url)

    # These variables were missing from our config.
    config['GIT_TOPLEVEL'] = path
    config['GIT_DIR'] = os.path.join(path, '.git')

    # Go back to the root of our git repo and make go on the export
    os.chdir(path)
    hg2git(config)

    return 0

if __name__ == '__main__':
    rval = 1

    try:
        rval = main()
    except Exception, e:
        sys.stderr.write('%s\n' % (str(e),))

    sys.exit(rval)
