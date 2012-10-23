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
from setuptools_git.utils import compose


def windecode(path):
    # We receive wonky filenames on Windows, probably because of
    # mysys-git's Unicode support.
    preferredencoding = locale.getpreferredencoding()
    if sys.version_info >= (3,):
        try:
            path = compose(path.decode('utf-8'))
        except UnicodeDecodeError:
            path = path.decode(preferredencoding)
    else:
        try:
            path = compose(path.decode('utf-8'))\
                .encode(preferredencoding)
        except UnicodeError:
            pass # Already in preferred encoding (hopefully)
    return path


def gitlsfiles(dirname=''):
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
    try:
        filenames = check_output(
            ['git', 'ls-files', '-z'], cwd=dirname or None, stderr=PIPE)
    except (CalledProcessError, OSError):
        # Setuptools mandates we fail silently
        raise StopIteration

    for filename in filenames.split(b('\x00')):
        if filename:
            if sys.platform == 'win32':
                yield windecode(filename)
            else:
                yield fsdecode(filename)

