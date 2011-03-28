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

GIT_LIBEXEC="$(git --exec-path)"

export PYTHONPATH="$GIT_LIBEXEC"/ghg:$GIT_LIBEXEC:$PYTHONPATH

if ! type python > /dev/null 2>&1 ; then
    echo "You must have python (>= 2.7 or >= 3.2) installed"
    exit 1
fi

if ! type hg > /dev/null 2>&1 ; then
    echo "You must have mercurial installed"
    exit 1
fi

if ! python $GIT_LIBEXEC/ghg/check.py ; then
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
        NONGIT_OK=Yes . git-sh-setup
        die "$USAGE"
        ;;
esac

. git-sh-setup

shift

exec git $GCMD "$@"
# vim: set noexpandtab:
