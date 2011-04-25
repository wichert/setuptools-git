#!/usr/bin/env python

"""
A hook into setuptools for Git.
"""

import os
from subprocess import CalledProcessError
from subprocess import PIPE
from distutils.log import warn

try:
    from subprocess import check_output
except ImportError:
    # BBB for python <2.7
    def check_output(*popenargs, **kwargs):
        from subprocess import Popen
        if 'stdout' in kwargs:
            raise ValueError(
                    'stdout argument not allowed, it will be overridden.')
        process = Popen(stdout=PIPE, *popenargs, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise CalledProcessError(retcode, cmd, output=output)
        return output


def gitlsfiles(dirname=''):
    try:
        if dirname:
            cwd = dirname
        else:
            cwd = None
            dirname = '.'
        dirname = os.path.realpath(dirname)
        git_top = check_output(['git', 'rev-parse', '--show-toplevel'],
                stderr=PIPE, cwd=cwd).strip()
        git_files = check_output(['git', 'ls-files'], cwd=git_top, stderr=PIPE)
        git_files = set([os.path.join(git_top, fn)
            for fn in git_files.splitlines()])
    except (CalledProcessError, OSError):
        # Something went terribly wrong but the setuptools doc says we
        # must be strong in the face of danger.  We shall not run away
        # in panic.
        warn('Error running git')
        raise StopIteration

    prefix_length = len(dirname) + 1
    for (root, dirs, files) in os.walk(dirname, followlinks=True):
        for file in files:
            filename = os.path.join(root, file)
            realname = os.path.realpath(filename)
            if realname in git_files:
                yield filename[prefix_length:]
