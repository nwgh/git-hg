#!/bin/sh
#
# Copyright (c) 2010, Nick Hurley
#
# This file is licensed under a slightly modified version of the GPL v2. See the
# file COPYING in the source distribution for details

USAGE="git hg <command> [options]"

. git-sh-setup

export PY_GIT_DIR="$(git rev-parse --git-dir)"
export PY_GIT_TOPLEVEL="$(git rev-parse --show-toplevel)"
export PY_GIT_EDITOR="$(git var GIT_EDITOR)"
export PY_GIT_AUTHOR_IDENT="$(git var GIT_AUTHOR_IDENT)"
export PY_GIT_COMMITTER_IDENT="$(git var GIT_COMMITTER_IDENT)"
export PY_GIT_CONFIG="$(git config -l)"
export PY_GIT_LIBEXEC="$(dirname $0)"

case "$1" in
	branch)
		git hg-branch "$@"
		;;
	checkout)
		git hg-checkout "$@"
		;;
	clone)
		git hg-clone "$@"
		;;
	init)
		git hg-init "$@"
		;;
	log)
		git hg-log "$@"
		;;
	push)
		git hg-push "$@"
		;;
	rebase)
		git hg-rebase "$@"
		;;
	*)
		die "$USAGE"
		;;
esac

exit $?
