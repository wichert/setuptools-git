#!/usr/bin/env python

"""
A hook into setuptools for Git.
"""

from subprocess import CalledProcessError
from subprocess import PIPE

from setuptools_git.utils import check_output
from setuptools_git.utils import b
from setuptools_git.utils import fsdecode


def list_git_files(cwd):
    # NB: passing the "-z" option to "git ls-files" below returns the
    # output as a blob of null-terminated filenames without
    # canonicalization or use of "-quoting.
    #
    # So we'll get back e.g.:
    #
    #'pyramid/tests/fixtures/static/h\xc3\xa9h\xc3\xa9.html'
    #
    # instead of:
    #
    #'"pyramid/tests/fixtures/static/h\\303\\251h\\303\\251.html"'
    #
    # for each file
    filenames = check_output(
        ['git', 'ls-files', '-z'], cwd=cwd, stderr=PIPE)

    for filename in filenames.split(b('\x00')):
        if filename:
            yield fsdecode(filename)


def gitlsfiles(dirname=''):
    if dirname:
        cwd = dirname
    else:
        cwd = None
        dirname = '.'

    try:
        for filename in list_git_files(cwd):
            yield filename
    except (CalledProcessError, OSError):
        # setuptools mandates to fail silently
        raise StopIteration

