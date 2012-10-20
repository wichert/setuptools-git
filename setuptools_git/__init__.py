#!/usr/bin/env python

"""
A hook into setuptools for Git.
"""

import os
import os.path
from subprocess import CalledProcessError
from subprocess import PIPE
from distutils.log import warn
from setuptools_git.compat import check_output
from setuptools_git.compat import b


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
    #
    # This is necessary for the matching done in the "if realname in
    # git_files" code in gitlsfiles to work properly.
    git_top = check_output(['git', 'rev-parse', '--show-toplevel'],
            stderr=PIPE, cwd=cwd).strip()
    ls = check_output(['git', 'ls-files', '-z'], cwd=git_top, stderr=PIPE)
    filenames = filter(None, ls.split(b('\x00'))) # filter None for trailing \x00
    git_files = set([os.path.join(git_top, fn) for fn in filenames])
    return git_files


def gitlsfiles(dirname=''):
    try:
        if dirname:
            cwd = dirname
        else:
            cwd = None
            dirname = '.'
        git_files = list_git_files(cwd)
    except (CalledProcessError, OSError):
        # Something went terribly wrong but the setuptools doc says we
        # must be strong in the face of danger.  We shall not run away
        # in panic.
        warn('Error running git')
        raise StopIteration

    # Include symlinked files and directories by their symlinked path
    dirname = os.path.realpath(dirname)
    prefix_length = len(dirname) + 1
    for (root, dirs, files) in os.walk(dirname, followlinks=True):
        for file in files:
            filename = os.path.join(root, file)
            realname = os.path.realpath(filename)
            if realname in git_files:
                yield filename[prefix_length:]
