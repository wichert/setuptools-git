# -*- coding: utf-8 -*-
import sys
import os
import tempfile
import unittest

from os.path import realpath, join
from setuptools_git.utils import fsencode
from setuptools_git.utils import fsdecode
from setuptools_git.utils import posix
from setuptools_git.utils import rmtree
from setuptools_git.utils import decompose
from setuptools_git.utils import hfs_quote


class GitTestCase(unittest.TestCase):

    def setUp(self):
        self.old_cwd = os.getcwd()
        self.directory = self.new_repo()

    def tearDown(self):
        os.chdir(self.old_cwd)
        rmtree(self.directory)

    def new_repo(self):
        from setuptools_git.utils import check_call
        directory = realpath(tempfile.mkdtemp())
        os.chdir(directory)
        check_call(['git', 'init', '--quiet', directory])
        return directory

    def create_file(self, *path):
        fd = open(join(*path), 'wt')
        fd.write('dummy\n')
        fd.close()

    def create_git_file(self, *path):
        from setuptools_git.utils import check_call
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
                set([fsencode(posix(realpath('root.txt')))]))

    def test_at_repo_root_with_subdir(self):
        self.create_git_file('root.txt')
        os.mkdir(join(self.directory, 'subdir'))
        self.create_git_file('subdir', 'entry.txt')
        self.assertEqual(
                self.list_git_files(self.directory),
                set([fsencode(posix(realpath(join('subdir', 'entry.txt')))),
                     fsencode(posix(realpath('root.txt')))]))

    def test_at_repo_subdir(self):
        self.create_git_file('root.txt')
        os.mkdir(join(self.directory, 'subdir'))
        self.create_git_file('subdir', 'entry.txt')
        self.assertEqual(
                self.list_git_files(join(self.directory, 'subdir')),
                set([fsencode(posix(realpath(join('subdir', 'entry.txt')))),
                     fsencode(posix(realpath('root.txt')))]))

    def test_nonascii_filename(self):
        filename = 'héhé.html'

        # HFS Plus uses decomposed UTF-8
        if sys.platform == 'darwin':
            filename = decompose(filename)

        # NTFS expects Windows-1252 path names
        if sys.platform == 'win32':
            if sys.version_info < (3,):
                # But mysys-git reinterprets them as UTF-8
                filename = filename.decode('cp1252').encode('utf-8')

        self.create_git_file(filename)

        self.assertEqual(
                [fn for fn in os.listdir(self.directory) if fn[0] != '.'],
                [filename])

        self.assertEqual(
                self.list_git_files(self.directory),
                set([fsencode(posix(realpath(filename)))]))

    def test_utf8_filename(self):
        if sys.version_info >= (3,):
            filename = 'héhé.html'.encode('utf-8')
        else:
            filename = 'héhé.html'

        # HFS Plus uses decomposed UTF-8
        if sys.platform == 'darwin':
            filename = decompose(filename)

        # Windows does not like byte filenames
        if sys.platform == 'win32':
            if sys.version_info >= (3,):
                filename = filename.decode('utf-8')

        self.create_git_file(filename)

        self.assertEqual(
                [fn for fn in os.listdir(self.directory) if fn[0] != '.'],
                [fsdecode(filename)])

        self.assertEqual(
                self.list_git_files(self.directory),
                set([fsencode(posix(realpath(filename)))]))

    def test_latin1_filename(self):
        if sys.version_info >= (3,):
            filename = 'héhé.html'.encode('latin-1')
        else:
            filename = 'h\xe9h\xe9.html'

        # HFS Plus quotes unknown bytes
        if sys.platform == 'darwin':
            filename = hfs_quote(filename)

        # Windows does not like byte filenames
        if sys.platform == 'win32':
            if sys.version_info >= (3,):
                filename = filename.decode('latin-1')

        self.create_git_file(filename)

        self.assertEqual(
                [fn for fn in os.listdir(self.directory) if fn[0] != '.'],
                [fsdecode(filename)])

        self.assertEqual(
                self.list_git_files(self.directory),
                set([fsencode(posix(realpath(filename)))]))

    if sys.platform != 'win32':

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
                rmtree(foreign)


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

    def test_nonascii_filename(self):
        filename = 'héhé.html'

        # HFS Plus uses decomposed UTF-8
        if sys.platform == 'darwin':
            filename = decompose(filename)

        self.create_git_file(filename)
        self.assertEqual(
                set(self.gitlsfiles()),
                set([filename]))

    def test_utf8_filename(self):
        if sys.version_info >= (3,):
            filename = 'héhé.html'.encode('utf-8')
        else:
            filename = 'héhé.html'

        # HFS Plus uses decomposed UTF-8
        if sys.platform == 'darwin':
            filename = decompose(filename)

        # Windows does not like byte filenames
        if sys.platform == 'win32':
            if sys.version_info >= (3,):
                filename = filename.decode('utf-8')

        self.create_git_file(filename)
        self.assertEqual(
                set(self.gitlsfiles()),
                set([fsdecode(filename)]))

    def test_latin1_filename(self):
        if sys.version_info >= (3,):
            filename = 'héhé.html'.encode('latin-1')
        else:
            filename = 'h\xe9h\xe9.html'

        # HFS Plus quotes unknown bytes
        if sys.platform == 'darwin':
            filename = hfs_quote(filename)

        # Windows does not like byte filenames
        if sys.platform == 'win32':
            if sys.version_info >= (3,):
                filename = filename.decode('latin-1')

        self.create_git_file(filename)
        self.assertEqual(
                set(self.gitlsfiles()),
                set([fsdecode(filename)]))

    if sys.platform != 'win32':

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
                rmtree(foreign)

