#!/usr/bin/env python
from distutils.core import setup

setup(name='ghg', version='0.1', description='Git-HG helper lib',
    author='Nick Hurley', author_email='hurley@todesschaf.org',
    url='https://github.com/todesschaf/git-hg', packages=['ghg'],
    package_dir={'ghg':'src/helpers'})
