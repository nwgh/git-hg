import os
import sys

def usage():
    raise Exception, 'git hg clone <repository> [<directory>]'

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        usage()
    url = sys.argv[1]
    if len(sys.argv) == 2:
        path = os.path.basename(url)
    else:
        path = sys.argv[3]

    # Create our git repo
    os.mkdir(path)
    os.chdir(path)
    os.system('git init')

    # Have to do this here so it can pick up the git env properly
    from git_py_setup import config

    # Create our bare hg repo under the git metadir
    os.chdir('.git')
    os.mkdir('hg')
    os.chdir('hg')
    os.system('hg clone -U "%s" repo' % url)

    return 0

if __name__ == '__main__':
    rval = 1
    try:
        rval = main()
    except Exception, e:
        print str(e)

    sys.exit(rval)
