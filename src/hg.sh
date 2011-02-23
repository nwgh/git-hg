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

if ! type python > /dev/null 2>&1 ; then
	echo "You must have python (>= 2.7 or >= 3.2) installed"
	exit 1
fi

if ! type hg > /dev/null 2>&1 ; then
	echo "You must have mercurial installed"
	exit 1
fi

if ! python $PY_GIT_LIBEXEC/git_hg_helpers/check.py ; then
	exit 1
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
