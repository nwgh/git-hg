PREFIX?=/usr/local
GIT_LIBEXEC?=${PREFIX}/libexec/git-core
GIT_MANDIR?=${PREFIX}/share/man/man1

all:

install: all
	install -d -m 0755 -o root ${GIT_LIBEXEC}/git_hg_helpers/
	install -m 0644 -o root src/helpers/* ${GIT_LIBEXEC}/git_hg_helpers/
	install -m 0644 -o root src/setup.py ${GIT_LIBEXEC}/git_py_setup.py
	install -m 0755 -o root src/hg.sh ${GIT_LIBEXEC}/git-hg
	install -m 0755 -o root src/clone.py ${GIT_LIBEXEC}/git-hg-clone
	install -m 0755 -o root src/fetch.py ${GIT_LIBEXEC}/git-hg-fetch
	install -m 0755 -o root src/pull.sh ${GIT_LIBEXEC}/git-hg-pull
	install -m 0755 -o root src/push.py ${GIT_LIBEXEC}/git-hg-push
	install -m 0644 -o root man/git-hg.1 ${GIT_MANDIR}/git-hg.1
