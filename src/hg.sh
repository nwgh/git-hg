#!/bin/sh
#
# Copyright (c) 2010, Nick Hurley
#
# This file is licensed under a slightly modified version of the GPL v2. See the
# file COPYING in the source distribution for details

USAGE="<command> [options]"

export PY_GIT_EDITOR="$(git var GIT_EDITOR)"
export PY_GIT_AUTHOR_IDENT="$(git var GIT_AUTHOR_IDENT)"
export PY_GIT_COMMITTER_IDENT="$(git var GIT_COMMITTER_IDENT)"
export PY_GIT_CONFIG="$(git config -l)"
export PY_GIT_LIBEXEC="$(dirname $0)"

PYVERSION="$(python -V 2>&1 | cut -d' ' -f2 | cut -d. -f1,2)"
PYMAJOR="$(echo $PYVERSION | cut -d. -f1)"
PYMINOR="$(echo $PYVERSION | cut -d. -f2)"

invalid_python() {
	echo "Python version 2.7 (or higher) or 3.2 (or higher) must be installed"
	exit 1
}

if [[ $PYMAJOR -eq 2 ]] ; then
	if [[ $PYMINOR -lt 7 ]] ; then
		invalid_python
	fi
else
	if [[ $PYMAJOR -eq 3 ]] ; then
		if [[ $PYMINOR -lt 2 ]] ; then
			invalid_python
		fi
	else
		invalid_python
	fi
fi

case "$1" in
	clone)
        NONGIT_OK=Yes
        GCMD="hg-clone"
        ;;
    fetch|pull|push)
        GCMD="hg-$1"
        ;;
	*)
		die "$USAGE"
		;;
esac

. git-sh-setup

shift

if [[ -z "$NONGIT_OK" ]] ; then
    export PY_GIT_DIR="$(git rev-parse --git-dir)"
    export PY_GIT_TOPLEVEL="$(git rev-parse --show-toplevel)"
fi

git $GCMD "$@"

exit $?
# vim: set noexpandtab:
