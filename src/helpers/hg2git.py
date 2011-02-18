import os
import subprocess
import sys
import time

__all__ = ['INFO', 'WARN', 'ERR', 'DEBUG_NAMES', 'DEBUG_LEVEL']

# Configuration for debugging
INFO = 0
WARN = 1
ERR = 2
DEBUG_NAMES = {INFO:'INFO', WARN:'WARN', ERR:'ERR'}
DEBUG_LEVELS = dict(((v, k) for k, v in DEBUG_NAMES.iteritems()))
DEBUG_LEVEL = ERR

def hg2git(config):
    """Using fast-export/fast-import, export a private hg repo into our current
    git repository. Also, do some nice logging so we know what happened.
    """
    helpers = os.path.join(config['GIT_LIBEXEC'], 'git_hg_helpers')
    hg_data = os.path.join(config['GIT_DIR'], 'hg')
    debugfile = os.path.join(hg_data, 'debug.log')
    debug = file(debugfile, 'w+')
    dlvl = os.getenv('GIT_HG_DEBUG')
    if dlvl in DEBUG_LEVELS:
        DEBUG_LEVEL = DEBUG_LEVELS[dlvl]

    debug.write('=' * 70)
    debug.write('\n')
    debug.write('STARTING HG->GIT EXPORT @ %s\n' % (time.ctime().upper(),))
    debug.write('\n')

    export_bin = os.path.join(helpers, 'git-hg-export.py')
    export_args = ['python', export_bin, hg_data, helpers, config['GIT_DIR']]
    import_args = ['git', 'fast-import']

    exporter = subprocess.Popen(export_args, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    importer = subprocess.Popen(import_args, stdin=exporter.stdout,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    exporter.wait()
    importer.wait()

    for line in exporter.stderr:
        if line.startswith('ERR'):
            sys.stderr.write(line)
        debug.write('EXPORTER: %s' % (line,))
    for line in importer.stdout:
        sys.stderr.write(line)
        debug.write('IMPORTER: %s' % (line,))

    debug.write('=' * 70)
    debug.write('\n')
    debug.write('\n')

    debug.close()
