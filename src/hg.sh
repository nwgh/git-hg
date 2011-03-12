#!/bin/sh
#
# Copyright (c) 2011 Nick Hurley <hurley at todesschaf dot org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of version 2 of the GNU General Public License as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

USAGE="<command> [options]"

export PY_GIT_EDITOR="$(git var GIT_EDITOR)"
export PY_GIT_AUTHOR_IDENT="$(git var GIT_AUTHOR_IDENT)"
export PY_GIT_COMMITTER_IDENT="$(git var GIT_COMMITTER_IDENT)"
export PY_GIT_CONFIG="$(git config -l)"
export PY_GIT_LIBEXEC="$(dirname $0)"
export PYTHONPATH="$PY_GIT_LIBEXEC"/ghg:$PY_GIT_LIBEXEC:$PYTHONPATH

if ! type python > /dev/null 2>&1 ; then
	echo "You must have python (>= 2.7 or >= 3.2) installed"
	exit 1
fi

if ! type hg > /dev/null 2>&1 ; then
	echo "You must have mercurial installed"
	exit 1
fi

if ! python $PY_GIT_LIBEXEC/ghg/check.py ; then
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
