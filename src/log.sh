#!/bin/sh
#
# Copyright (c) 2010 Nick Hurley
#
# This file is licensed under a slightly modified version of the GPL v2. See the
# file COPYING in the source distribution for details

USAGE="git hg log ['git log' options]"

. git-sh-setup

git log --show-notes=git-hg "$@"
