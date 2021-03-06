PREFIX?=/usr/local
GIT_LIBEXEC?=${PREFIX}/libexec/git-core
MANDIR?=${PREFIX}/share/man/man1
BINDIR?=${GIT_LIBEXEC}
OWNER?=root

all:

install-lib:
	python ./setup.py install

install-bin: all install-lib
	install -m 0755 -o ${OWNER} src/hg.sh ${BINDIR}/git-hg
	install -m 0755 -o ${OWNER} src/clone.py ${BINDIR}/git-hg-clone
	install -m 0755 -o ${OWNER} src/fetch.py ${BINDIR}/git-hg-fetch
	install -m 0755 -o ${OWNER} src/pull.py ${BINDIR}/git-hg-pull
	install -m 0755 -o ${OWNER} src/push.py ${BINDIR}/git-hg-push

install: all install-bin install-lib
	install -m 0644 -o ${OWNER} man/git-hg.1 ${MANDIR}/git-hg.1
