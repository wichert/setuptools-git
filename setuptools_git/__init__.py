#!/usr/bin/env python

"""
A hook into setuptools for Git.
"""
import sys
import locale

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
            if sys.platform == 'win32':
                # msys-git on Windows returns UTF-8
                if sys.version_info >= (3,):
                    yield filename.decode('utf-8')
                else:
                    preferredencoding = locale.getpreferredencoding()
                    yield filename.decode('utf-8').encode(preferredencoding)
            else:
                yield fsdecode(filename)


def gitlsfiles(dirname=''):
    try:
        for filename in list_git_files(dirname or None):
            yield filename
    except (CalledProcessError, OSError):
        # setuptools mandates to fail silently
        raise StopIteration

