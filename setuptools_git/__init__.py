#!/usr/bin/env python

"""
A hook into setuptools for Git.
"""
import sys
import os
import locale
import posixpath

from os.path import realpath, join
from subprocess import CalledProcessError
from subprocess import PIPE

from setuptools_git.utils import check_output
from setuptools_git.utils import b
from setuptools_git.utils import fsdecode
from setuptools_git.utils import posix
from setuptools_git.utils import compose
from setuptools_git.utils import hfs_quote


def windecode(path):
    # We receive the raw bytes from Git and have to decode by hand.
    # Msysgit returns UTF-8 encoded bytes except when it doesn't.
    preferredencoding = locale.getpreferredencoding()
    if sys.version_info >= (3,):
        try:
            path = compose(path.decode('utf-8'))
        except UnicodeDecodeError:
            path = path.decode(preferredencoding)
    else:
        try:
            path = compose(path.decode('utf-8')).encode(preferredencoding)
        except UnicodeError:
            pass # Already in preferred encoding (hopefully)
    return path


def decode(path):
    if sys.platform == 'win32':
        return windecode(path)
    return compose(fsdecode(path))


def quote(path):
    if sys.platform == 'darwin':
        return hfs_quote(path)
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
        topdir = check_output(
            ['git', 'rev-parse', '--show-toplevel'], cwd=dirname or None,
            stderr=PIPE).strip()

        if sys.platform == 'win32':
            cwd = windecode(topdir)
        else:
            cwd = topdir

        filenames = check_output(
            ['git', 'ls-files', '-z'], cwd=cwd, stderr=PIPE)
    except (CalledProcessError, OSError):
        # Setuptools mandates we fail silently
        return set()

    return set(decode(quote(posixpath.join(topdir, x))) for x in filenames.split(b('\x00')) if x)


def listfiles(dirname=''):
    filenames = gitlsfiles(dirname)
    dirnames = set(posixpath.dirname(x) for x in filenames)

    cwd = realpath(dirname or os.curdir)
    prefix_length = len(cwd) + 1

    if sys.version_info >= (2, 6):
        walker = os.walk(cwd, followlinks=True)
    else:
        walker = os.walk(cwd)

    for root, dirs, files in walker:
        if dirs:
            dirs[:] = [x for x in dirs if compose(posix(realpath(join(root, x)))) in dirnames]
        for file in files:
            filename = join(root, file)
            if compose(posix(realpath(filename))) in filenames:
                yield filename[prefix_length:]


if __name__ == '__main__':
    if len(sys.argv) > 1:
        dirname = sys.argv[1]
    else:
        dirname = ''
    for filename in listfiles(dirname):
        print(filename)

