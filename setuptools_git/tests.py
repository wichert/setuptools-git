# -*- coding: utf-8 -*-
import sys
import os
import shutil
import unicodedata
import tempfile
import unittest

from os.path import realpath, join
from setuptools_git.compat import url_quote
from setuptools_git.compat import fsencode
from setuptools_git.compat import fsdecode

if sys.version_info >= (3,):
    unicode = str


# HFS Plus returns decomposed UTF-8
def decompose(path):
    if isinstance(path, unicode):
        return unicodedata.normalize('NFD', path)
    try:
        path = path.decode('utf-8')
        path = unicodedata.normalize('NFD', path)
        path = path.encode('utf-8')
    except UnicodeError:
        pass # Not UTF-8
    return path


# HFS Plus quotes unknown bytes like so: %F6
def hfs_quote(path):
    if isinstance(path, unicode):
        raise TypeError('bytes are required')
    try:
        path.decode('utf-8')
    except UnicodeDecodeError:
        path = url_quote(path) # Not UTF-8
        if sys.version_info >= (3,):
            path = path.encode('ascii')
    return path


class GitTestCase(unittest.TestCase):

    def setUp(self):
        self.old_cwd = os.getcwd()
        self.directory = self.new_repo()

    def tearDown(self):
        shutil.rmtree(self.directory)
        os.chdir(self.old_cwd)

    def new_repo(self):
        from setuptools_git.compat import check_call
        directory = realpath(tempfile.mkdtemp())
        os.chdir(directory)
        check_call(['git', 'init', '--quiet', directory])
        return directory

    def create_file(self, *path):
        fd = open(join(*path), 'wt')
        fd.write('dummy\n')
        fd.close()

    def create_git_file(self, *path):
        from setuptools_git.compat import check_call
        filename = join(*path)
        fd = open(filename, 'wt')
        fd.write('dummy\n')
        fd.close()
        check_call(['git', 'add', filename])
        check_call(['git', 'commit', '--quiet', '-m', 'add new file'])


class list_git_files_tests(GitTestCase):

    def list_git_files(self, *a, **kw):
        from setuptools_git import list_git_files
        return list_git_files(*a, **kw)

    def test_at_repo_root(self):
        self.create_git_file('root.txt')
        self.assertEqual(
                self.list_git_files(self.directory),
                set([fsencode(realpath('root.txt'))]))

    def test_at_repo_root_with_subdir(self):
        self.create_git_file('root.txt')
        os.mkdir(join(self.directory, 'subdir'))
        self.create_git_file('subdir', 'entry.txt')
        self.assertEqual(
                self.list_git_files(self.directory),
                set([fsencode(realpath(join('subdir', 'entry.txt'))),
                     fsencode(realpath('root.txt'))]))

    def test_at_repo_subdir(self):
        self.create_git_file('root.txt')
        os.mkdir(join(self.directory, 'subdir'))
        self.create_git_file('subdir', 'entry.txt')
        self.assertEqual(
                self.list_git_files(join(self.directory, 'subdir')),
                set([fsencode(realpath(join('subdir', 'entry.txt'))),
                     fsencode(realpath('root.txt'))]))

    def test_utf8_filename(self):
        filename = 'héhé.html'

        # HFS Plus uses decomposed UTF-8
        if sys.platform == 'darwin':
            filename = decompose(filename)

        self.create_git_file(filename)
        self.assertEqual(
                self.list_git_files(self.directory),
                set([fsencode(realpath(filename))]))

    def test_latin1_filename(self):
        if sys.version_info >= (3,):
            filename = 'héhé.html'.encode('latin-1')
        else:
            filename = 'h\xe9h\xe9.html'

        # HFS Plus quotes unknown bytes
        if sys.platform == 'darwin':
            filename = hfs_quote(filename)

        self.create_git_file(filename)
        self.assertEqual(
                self.list_git_files(self.directory),
                set([fsencode(realpath(filename))]))

    def test_directory_symlink(self):
        os.mkdir(join(self.directory, 'subdir'))
        self.create_git_file('subdir', 'entry.txt')
        os.mkdir(join(self.directory, 'package'))
        self.create_git_file('package', 'root.txt')
        os.symlink(
                join(self.directory, 'subdir'),
                join(self.directory, 'package', 'data'))
        self.assertEqual(
                set(self.list_git_files(join(self.directory, 'package'))),
                set([fsencode(realpath(join('subdir', 'entry.txt'))),
                     fsencode(realpath(join('package', 'root.txt')))]))

    def test_foreign_repo_symlink(self):
        os.mkdir(join(self.directory, 'subdir'))
        self.create_git_file('subdir', 'entry.txt')
        foreign = self.new_repo()
        try:
            os.mkdir(join(foreign, 'package'))
            self.create_git_file('package', 'root.txt')
            os.symlink(
                    join(self.directory, 'subdir'),
                    join(foreign, 'package', 'data'))
            self.assertEqual(
                    set(self.list_git_files(join(foreign, 'package'))),
                    set([fsencode(realpath(join('package', 'root.txt')))]))
        finally:
            shutil.rmtree(foreign)


class gitlsfiles_tests(GitTestCase):

    def gitlsfiles(self, *a, **kw):
        from setuptools_git import gitlsfiles
        return gitlsfiles(*a, **kw)

    def test_empty_dirname(self):
        self.create_git_file('root.txt')
        self.assertEqual(
                set(self.gitlsfiles()),
                set(['root.txt']))

    def test_specify_full_path(self):
        self.create_git_file('root.txt')
        os.chdir(self.old_cwd)
        self.assertEqual(
                set(self.gitlsfiles(self.directory)),
                set(['root.txt']))

    def test_at_repo_root_with_subdir(self):
        self.create_git_file('root.txt')
        os.mkdir(join(self.directory, 'subdir'))
        self.create_git_file('subdir', 'entry.txt')
        self.assertEqual(
                set(self.gitlsfiles()),
                set([join('subdir', 'entry.txt'),
                     'root.txt']))

    def test_at_repo_subdir(self):
        self.create_git_file('root.txt')
        os.mkdir(join(self.directory, 'subdir'))
        self.create_git_file('subdir', 'entry.txt')
        os.chdir('subdir')
        self.assertEqual(
                set(self.gitlsfiles()),
                set(['entry.txt']))

    def test_utf8_filename(self):
        filename = 'héhé.html'

        # HFS Plus uses decomposed UTF-8
        if sys.platform == 'darwin':
            filename = decompose(filename)

        self.create_git_file(filename)
        self.assertEqual(
                set(self.gitlsfiles()),
                set([filename]))

    def test_latin1_filename(self):
        if sys.version_info >= (3,):
            filename = 'héhé.html'.encode('latin-1')
        else:
            filename = 'h\xe9h\xe9.html'

        # HFS Plus quotes unknown bytes
        if sys.platform == 'darwin':
            filename = hfs_quote(filename)

        self.create_git_file(filename)
        self.assertEqual(
                set(self.gitlsfiles()),
                set([fsdecode(filename)]))

    def test_directory_symlink(self):
        os.mkdir(join(self.directory, 'subdir'))
        self.create_git_file('subdir', 'entry.txt')
        os.mkdir(join(self.directory, 'package'))
        self.create_git_file('package', 'root.txt')
        os.symlink(
                join(self.directory, 'subdir'),
                join(self.directory, 'package', 'data'))
        os.chdir('package')
        self.assertEqual(
                set(self.gitlsfiles()),
                set([join('data', 'entry.txt'),
                     'root.txt']))

    def test_foreign_repo_symlink(self):
        os.mkdir(join(self.directory, 'subdir'))
        self.create_git_file('subdir', 'entry.txt')
        foreign = self.new_repo()
        try:
            os.mkdir(join(foreign, 'package'))
            self.create_git_file('package', 'root.txt')
            os.symlink(
                    join(self.directory, 'subdir'),
                    join(foreign, 'package', 'data'))
            os.chdir(join(foreign, 'package'))
            self.assertEqual(
                    set(self.gitlsfiles()),
                    set(['root.txt']))
        finally:
            shutil.rmtree(foreign)

