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

def update_heads(headsfile):
    with open(headsfile, 'w') as f:
        heads = subprocess.Popen(['git', 'branch'], stdout=subprocess.PIPE)
        for h in heads.stdout:
            head = h.strip()
            if head.startswith('hg/'):
                rp = subprocess.Popen(['git', 'rev-parse', head],
                    stdout=subprocess.PIPE)
                sha = rp.stdout.readline().strip()
                rp.wait()
                f.write(':%s %s\n' % (head, sha))
        heads.wait()

def merge_marks(marksfile, gfimarks):
    if os.path.exists(marksfile):
        marks = {}
        with open(marksfile) as f:
            for line in f:
                marks[line] = True
        with open(gfimarks) as f:
            for line in f:
                marks[line] = True
        os.unlink(gfimarks)
        with open(marksfile, 'w') as f:
            for m in marks.keys():
                f.write(m)
    else:
        os.rename(gfimarks, marksfile)

def hg2git(config):
    """Using fast-export/fast-import, export a private hg repo into our current
    git repository. Also, do some nice logging so we know what happened.
    """
    helpers = os.path.join(config['GIT_LIBEXEC'], 'git_hg_helpers')
    debugfile = os.path.join(config['HG_META'], 'debug.log')
    gfimarks = os.path.join(config['HG_META'], 'gfimarks')
    debug = file(debugfile, 'w+')
    dlvl = os.getenv('GIT_HG_DEBUG')
    if dlvl in DEBUG_LEVELS:
        DEBUG_LEVEL = DEBUG_LEVELS[dlvl]

    debug.write('=' * 70)
    debug.write('\n')
    debug.write('STARTING HG->GIT EXPORT @ %s\n' % (time.ctime().upper(),))
    debug.write('\n')

    export_bin = os.path.join(helpers, 'git-hg-export.py')
    export_args = ['python', export_bin, config['HG_REPO'], config['HG_MAP'],
                   config['HG_TIP'], config['HG_MARKS'], config['HG_HEADS'],
                   helpers]
    import_args = ['git', 'fast-import', '--export-marks=%s' % (gfimarks,)]

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
        debug.write('IMPORTER: %s' % (line,))

    debug.write('=' * 70)
    debug.write('\n')
    debug.write('\n')

    debug.close()

    os.chdir(config['GIT_TOPLEVEL'])
    update_heads(config['HG_HEADS'])
    merge_marks(config['HG_MARKS'], gfimarks)
