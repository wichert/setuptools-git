#!/usr/bin/env python

"""
A hook into setuptools for Git.
"""

import os
from subprocess import CalledProcessError
from subprocess import PIPE
from distutils.log import warn
from setuptools_git.compat import check_output


def is_child(parent, sub):
    return parent != sub and \
            sub.startswith(parent) and \
            sub[len(parent)] == os.path.sep


def list_git_files(cwd):
    git_top = check_output(['git', 'rev-parse', '--show-toplevel'],
            stderr=PIPE, cwd=cwd).strip()
    git_files = check_output(['git', 'ls-files'], cwd=git_top, stderr=PIPE)
    git_files = set([os.path.join(git_top, fn)
        for fn in git_files.splitlines()])
    return git_files


def gitlsfiles(dirname=''):
    try:
        if dirname:
            cwd = dirname
        else:
            cwd = None
            dirname = '.'
        package_root = os.path.realpath(dirname)
        git_files = list_git_files(cwd)
    except (CalledProcessError, OSError):
        # Something went terribly wrong but the setuptools doc says we
        # must be strong in the face of danger.  We shall not run away
        # in panic.
        warn('Error running git')
        raise StopIteration

    git_dirs = set([os.path.dirname(f) for f in git_files])
    prefix_length = len(package_root) + 1
    result = []

    for (root, dirs, files) in os.walk(package_root):
        for dir in dirs:
            dirname = os.path.join(root, dir)
            realname = os.path.normpath(dirname)
            if not os.path.islink(realname):
                continue
            elif realname not in git_files:
                continue

            target = os.readlink(realname)
            if not os.path.isabs(target):
                target = os.path.join(os.path.dirname(realname), target)
            target = os.path.normpath(target)
            if target not in git_dirs:
                continue

            prefix = dirname[prefix_length:]
            if is_child(package_root, target):
                result.append(prefix)
                continue

            # Special case: symlink pointing to a directory inside the git
            # repo, but outside the package. In that case we walk over the
            # directory and add its contents
            for (subroot, subdirs, subfiles) in os.walk(target):
                prefix = dirname[prefix_length:]
                for file in subfiles:
                    filename = os.path.join(subroot, file)
                    filename = os.path.normpath(filename)
                    if filename in git_files:
                        result.append(prefix + filename[len(target):])

        for file in files:
            filename = os.path.join(root, file)
            filename = os.path.normpath(filename)
            if filename not in git_files:
                continue

            result.append(filename[prefix_length:])

    return result
