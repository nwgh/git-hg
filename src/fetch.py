#!/usr/bin/env python
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

import argparse
import os
import sys

import ghg
import pgl

@pgl.main
def main():
    ap = argparse.ArgumentParser(description='Fetch updates from hg',
        prog='git hg fetch')
    args = ap.parse_args(sys.argv[1:])

    # Make sure our config dict contains the stuff we need
    ghg.include_hg_setup()

    # Do some sanity checks to make sure we're where we think we are
    ghg.ensure_is_ghg()

    # Update the private remote git repo
    ghg.update_remote()

    # Now fetch those changes into our local repo
    os.system('git fetch hg')

    return 0
