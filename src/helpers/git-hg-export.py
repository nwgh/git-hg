#!/usr/bin/env python

# Copyright (c) 2007, 2008 Rocco Rutte <pdmef@gmx.net> and others.
# License: MIT <http://www.opensource.org/licenses/mit-license.php>
# Fairly strongly modified by Nick Hurley <hurley@todesschaf.org>

from mercurial import repo, hg, node, ui
import re
import sys
import os

def debug(level, msg):
    """Print information to stderr only if the debug level is met"""
    if level >= DEBUG_LEVEL:
        sys.stderr.write('%s: %s\n' % (DEBUG_NAMES[level], msg))

def wr(data):
    """Write data to stdout for consumption by git-fast-import"""
    sys.stdout.write('%s\n' % (data,))

def setup_repo(url):
    """Configure the hg repository information appropriately"""
    try:
        myui = ui.ui(interactive=False)
    except TypeError:
        myui = ui.ui()
        myui.setconfig('ui', 'interactive', 'off')

    return (myui, hg.repository(myui,url))

# See if user field has email address
__user_re = re.compile('([^<]+) (<[^>]+>)$')

# Clean up user names
__user_clean_re = re.compile('^["]([^"]+)["]$')

def fixup_user(user):
    """Take an hg username string and massage it into a format git can use"""
    name, mail, m = '', '', __user_re.match(user)
    if m == None:
        # if we don't have 'Name <mail>' syntax, use 'user
        # <devnull@localhost>' if use contains no '@' and
        # 'user <user>' otherwise
        name = user

        if '@' not in user:
            mail='<devnull@localhost>'
        else:
            mail='<%s>' % user
    else:
        # if we have 'Name <mail>' syntax, everything is fine
        name, mail = m.group(1), m.group(2)

    # remove any silly quoting from username
    m2 = __user_clean_re.match(name)

    if m2 != None:
      name = m2.group(1)

    return '%s %s' % (name, mail)

def get_branch(name):
    """Figure out what branch name to use (adjusting default->master, etc).
    We put all exported branches in the "hg/" namespace"""
    # 'HEAD' is the result of a bug in mutt's cvs->hg conversion,
    # other CVS imports may need it, too
    if name == 'HEAD' or name == 'default' or name == '':
        name = 'master'

    return 'hg/%s' % (name,)

def get_changeset(ui, repo, revision):
    """Get all the relevant information associated with a changeset in hg"""
    node = repo.lookup(revision)
    manifest, user, tinfo, files, desc, extra = repo.changelog.read(node)

    time, timezone = tinfo
    tz = "%+03d%02d" % (-timezone / 3600, ((-timezone % 3600) / 60))
    tinfo = (time, tz)

    fixed_user = fixup_user(user)

    branch = get_branch(extra.get('branch', 'master'))

    return (node, manifest, fixed_user, tinfo, files, desc, branch, extra)

def load_cache(filename, get_key=lambda k: k):
    """Read information from a cache file on disk, massaging as necessary"""
    cache = {}
    if not os.path.exists(filename):
      return cache

    f = open(filename, 'r')
    l = 0
    for line in f.readlines():
        l += 1
        fields = line.split(' ')
        if not fields or len(fields) != 2 or fields[0][0] != ':':
            debug(INFO, '%s:%d: Invalid format' % (filename, l))
            continue

        # put key:value in cache, key without ^:
        cache[get_key(fields[0][1:])] = fields[1].split('\n')[0]

    f.close()

    return cache

def save_cache(filename, cache):
    """Write an in-memory cache to permanent storage"""
    f = open(filename, 'w+')
    for k, v in cache.iteritems():
        f.write(':%s %s\n' % (str(k), str(v)))
    f.close()

def get_git_sha1(name, reftype='heads'):
    """Figure out the sha1 of the head of a ref in git"""
    try:
        # use git-rev-parse to support packed refs
        cmd = "GIT_DIR='%s' git rev-parse --verify refs/%s/%s 2>/dev/null" % \
            (sys.argv[3], reftype, name)
        p = os.popen(cmd)
        l = p.readline()
        p.close()
        if not l:
            return None
        return l[:40]
    except IOError:
        return None

def gitmode(flags):
    """Return the git mode string based on file type"""
    if 'l' in flags:
        return '120000'
    if 'x' in flags:
        return '100755'
    return '100644'

# insert 'checkpoint' command after this many commits or none at all if 0
__checkpoint_ncmds = 0

def checkpoint(ncmds):
    """Write a checkpoint every so many commands"""
    ncmds += 1
    if __checkpoint_ncmds > 0 and not ncmds % __checkpoint_ncmds:
        debug(INFO, 'Checkpoint after %d commits' % (ncmds,))
        wr('checkpoint')
        wr('')
    return ncmds

def revnum_to_revref(rev, old_marks):
    """Convert an hg revnum to a git-fast-import rev reference (a SHA1
    or a mark)"""
    r = old_marks.get(rev)
    if not r:
        r = ':%d' % (rev + 1)
    return r

def file_mismatch(f1, f2):
    """See if two revisions of a file are unequal."""
    return node.hex(f1) != node.hex(f2)

def split_dict(dleft, dright, l=None, c=None, r=None, match=file_mismatch):
    """Loop over our repository and find all changed and missing files."""
    if l is None:
        l = []
    if c is None:
        c = []
    if r is None:
        r = []

    for left in dleft.keys():
        right = dright.get(left, None)
        if right is None:
            # we have the file but our parent hasn't: add to left set
            l.append(left)
        elif file_mismatch(dleft[left], right):
            # we have it but checksums mismatch: add to center set
            c.append(left)
    for right in dright.keys():
        left = dleft.get(right, None)
        if left is None:
            # if parent has file but we don't: add to right set
            r.append(right)

    return (l, c, r)

def get_filechanges(repo, revision, parents, mleft):
    """Given some repository and revision, find all changed/deleted files."""
    l, c, r = [], [], []
    for p in parents:
        if p < 0:
            continue
        mright = repo.changectx(p).manifest()
        l, c, r = split_dict(mleft, mright, l, c, r)

    l.sort()
    c.sort()
    r.sort()

    return (l, c, r)

def export_file_contents(ctx, manifest, files):
    """Export the contents of a file in fast-export format"""
    count = 0
    nfiles = len(files)
    for f in files:
        # Skip .hgtags files. They only get us in trouble.
        if f == ".hgtags":
            debug(INFO, 'Skip hgtags file')
            continue
        d = ctx.filectx(f).data()
        wr('M %s inline %s' % (gitmode(manifest.flags(f)), f))
        wr('data %d' % (len(d),))
        wr(d)
        count += 1
        debug(INFO, 'Exported %d/%d files' % (count, nfiles))

__sanitize_re = re.compile('([[ ~^:?*]|\.\.)')
__singleunder_re = re.compile('_+')

def sanitize_name(name, what="branch"):
    """Sanitize input roughly according to git-check-ref-format(1)"""
    def fixup_dot(name):
        if name[0] == '.':
            return '_' + name[1:]
        return name

    n = name
    n = __sanitize_re.sub('_', n)

    if n[-1] == '/':
        n = n[:-1] + '_'

    n = '/'.join(map(fixup_dot, n.split('/')))
    n = __singleunder_re.sub('_', n)

    if n != name:
        debug(WARN, 'Sanitized %s [%s] to [%s]' % (what, name, n))

    return n

def export_commit(ui, repo, revision, old_marks, nrevs, ncmds, brmap):
    """Export a commit in fast-export format"""
    revnode, _, user, tinfo, files, desc, branch, _ = get_changeset(ui, repo,
        revision)
    time, tz = tinfo

    branch = brmap.setdefault(branch, sanitize_name(branch))

    wr('commit refs/heads/%s' % (branch,))
    wr('mark :%d' % (revision + 1,))
    wr('committer %s %d %s' % (user, time, tz))
    wr('data %d' % (len(desc) + 1)) # wtf?
    wr(desc)
    wr('')

    parents = [p for p in repo.changelog.parentrevs(revision) if p >= 0]

    # Sort the parents based on revision ids so that we always get the
    # same resulting git repo, no matter how the revisions were
    # numbered.
    parents.sort(key=repo.changelog.node, reverse=True)

    ctx = repo.changectx(str(revision))
    manifest = ctx.manifest()
    added = []
    changed = []
    removed = []
    revtype = ''

    if not parents:
        # first revision: feed in full manifest
        added = manifest.keys()
        added.sort()
        revtype = 'full'
    else:
        wr('from %s' % revnum_to_revref(parents[0], old_marks))
        if len(parents) == 1:
            # later non-merge revision: feed in changed manifest
            # if we have exactly one parent, just take the changes from the
            # manifest without expensively comparing checksums
            f = repo.status(repo.lookup(parents[0]), revnode)[:3]
            added, changed, removed = f[1], f[0], f[2]
            revtype = 'simple delta'
        else: # a merge with two parents
            wr('merge %s' % revnum_to_revref(parents[1], old_marks))
            # later merge revision: feed in changed manifest
            # for many files comparing checksums is expensive so only do it for
            # merges where we really need it due to hg's revlog logic
            added, changed, removed = get_filechanges(repo, revision, parents,
                manifest)
            revtype = 'thorough delta'

    debug(INFO, '%s: Exporting %s revision %d/%d with %d/%d/%d '
        'added/changed/removed files' % (branch, revtype, revision + 1, nrevs,
        len(added), len(changed), len(removed)))

    for r in removed:
        wr('D %s' % (r,))
    export_file_contents(ctx, manifest, added)
    export_file_contents(ctx, manifest, changed)
    wr('')

    return checkpoint(ncmds)

def export_tags(ui, repo, old_marks, mapping_cache, ncmds):
    """Export all tags in fast-export format"""
    l = repo.tagslist()
    for tag, node in l:
        tag = sanitize_name(tag, "tag")

        # ignore latest revision
        if tag == 'tip':
            continue

        # ignore tags to nodes that are missing (ie, 'in the future')
        if node.encode('hex_codec') not in mapping_cache:
            debug(INFO, 'Tag %s refers to unseen node %s' %
                (tag, node.encode('hex_codec')))
            continue

        rev = int(mapping_cache[node.encode('hex_codec')])

        ref = revnum_to_revref(rev, old_marks)
        if ref == None:
            debug(WARN, 'Failed to find reference for creating tag '
                '%s at r%d' % (tag, rev))
            continue

        debug(INFO, 'Exporting tag [%s] at [hg r%d] [git %s]' % (tag, rev, ref))

        wr('reset refs/tags/%s' % tag)
        wr('from %s' % ref)
        wr('')

        ncmds = checkpoint(ncmds)

    return ncmds

def verify_heads(ui, repo, cache):
    """Make sure there are no detached heads, and that our git branches have
    not been changed outside the export system"""
    branches = repo.branchtags()
    branches = [b[0] for b in branches.items()]
    branches.sort()

    # get list of hg's branches to verify, don't take all git has
    for b in branches:
        b = get_branch(b)
        sha1 = get_git_sha1(b)
        c = cache.get(b)
        if sha1 != c:
            debug(ERR, 'Branch %s modified outside git-hg (repo:%s, '
                'cache: %s)' % (b, sha1, c))
            return False

    # verify that branch has exactly one head
    seen_branches = {}
    for h in repo.heads():
        branch = get_changeset(ui, repo, h)[6]

        if branch in seen_branches:
            debug(ERR, 'Repository has at least one unnamed head: '
                'hg r%s' % (repo.changelog.rev(h),))
            return False

        seen_branches[branch] = True

    return True

# Files containing metadata related to the export process
MARKSFILE = None
MAPPINGFILE = None
HEADSFILE = None
TIPFILE = None

def export_repo(repourl):
    """Export a hg repo in fast-export format"""
    old_marks = load_cache(MARKSFILE, lambda s: int(s) - 1)
    mapping_cache = load_cache(MAPPINGFILE)
    heads_cache = load_cache(HEADSFILE)
    state_cache = load_cache(TIPFILE)

    ui, repo = setup_repo(repourl)

    if not verify_heads(ui, repo, heads_cache):
        return 1

    try:
        tip = repo.changelog.count()
    except AttributeError:
        tip = len(repo)

    firstrev = int(state_cache.get('tip', 0))
    lastrev = tip

    for rev in range(0, lastrev):
        revnode = get_changeset(ui, repo, rev)[0]
        mapping_cache[revnode.encode('hex_codec')] = str(rev)

    ncmds = 0
    brmap = {}
    for rev in range(firstrev, lastrev):
        ncmds = export_commit(ui, repo, rev, old_marks, lastrev, ncmds, brmap)

    state_cache['tip'] = lastrev
    state_cache['repo'] = repourl
    save_cache(TIPFILE, state_cache)
    save_cache(MAPPINGFILE, mapping_cache)

    ncmds = export_tags(ui, repo, old_marks, mapping_cache, ncmds)

    debug(INFO, '')
    debug(INFO, 'Issued %d commands' % (ncmds,))

    return 0

if __name__ == '__main__':
    rval = 1

    MAPPINGFILE = sys.argv[2]
    TIPFILE = sys.argv[3]
    MARKSFILE = sys.argv[4]
    HEADSFILE = sys.argv[5]

    sys.path.insert(0, sys.argv[6])
    from hg2git import *

    try:
        rval = export_repo(sys.argv[1])
    except Exception, e:
        debug(ERR, str(e))

    sys.exit(rval)
