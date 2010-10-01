PREFIX?=/usr/local
GIT_LIBEXEC?=${PREFIX}/libexec/git-core
GIT_MANDIR?=${PREFIX}/share/man/man1

all:

install: all
	install -m 0644 -o root src/setup.py ${GIT_LIBEXEC}/git_py_setup.py
	install -m 0755 -o root src/hg.sh ${GIT_LIBEXEC}/git-hg
	install -m 0755 -o root src/branch.py ${GIT_LIBEXEC}/git-hg-branch
	install -m 0755 -o root src/checkout.py ${GIT_LIBEXEC}/git-hg-checkout
	install -m 0755 -o root src/clone.py ${GIT_LIBEXEC}/git-hg-clone
	install -m 0755 -o root src/init.py ${GIT_LIBEXEC}/git-hg-init
	install -m 0755 -o root src/log.sh ${GIT_LIBEXEC}/git-hg-log
	install -m 0755 -o root src/push.py ${GIT_LIBEXEC}/git-hg-push
	install -m 0755 -o root src/rebase.py ${GIT_LIBEXEC}/git-hg-rebase
	install -m 0644 -o root man/git-hg.1 ${GIT_MANDIR}/git-hg.1
