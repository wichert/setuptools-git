# -*- coding: utf-8 -*-
import unittest


class GitTestCase(unittest.TestCase):

    def setUp(self):
        import os
        self.old_cwd = os.getcwd()
        self.directory = self.new_repo()

    def tearDown(self):
        import os
        import shutil
        shutil.rmtree(self.directory)
        os.chdir(self.old_cwd)

    def new_repo(self):
        import os
        import tempfile
        from setuptools_git.compat import check_call
        directory = tempfile.mkdtemp()
        os.chdir(directory)
        check_call(['git', 'init', '--quiet', directory])
        return directory

    def create_file(self, *path):
        import os.path
        fd = open(os.path.join(*path), 'wt')
        print >>fd, 'dummy'
        fd.close()

    def create_git_file(self, *path):
        import os.path
        from setuptools_git.compat import check_call
        filename = os.path.join(*path)
        fd = open(filename, 'wt')
        print >>fd, 'dummy'
        fd.close()
        check_call(['git', 'add', filename])
        check_call(['git', 'commit', '--quiet', '-m', 'add new file'])


class list_git_files_tests(GitTestCase):

    def list_git_files(self, *a, **kw):
        from setuptools_git import list_git_files
        return list_git_files(*a, **kw)

    def test_at_repo_root(self):
        import os.path
        self.create_git_file('root.txt')
        self.assertEqual(
                self.list_git_files(self.directory),
                set([os.path.realpath('root.txt')]))

    def test_at_repo_root_with_subdir(self):
        import os
        import os.path
        self.create_git_file('root.txt')
        os.mkdir(os.path.join(self.directory, 'subdir'))
        self.create_git_file('subdir', 'entry.txt')
        self.assertEqual(
                self.list_git_files(self.directory),
                set([os.path.realpath('root.txt'),
                     os.path.realpath(os.path.join('subdir', 'entry.txt'))]))

    def test_at_repo_subdir(self):
        import os
        import os.path
        self.create_git_file('root.txt')
        os.mkdir(os.path.join(self.directory, 'subdir'))
        self.create_git_file('subdir', 'entry.txt')
        self.assertEqual(
                self.list_git_files(os.path.join(self.directory, 'subdir')),
                set([os.path.realpath('root.txt'),
                     os.path.realpath(os.path.join('subdir', 'entry.txt'))]))

    def test_nonascii_filename(self):
        import os.path
        self.create_git_file('héhé.html')
        result = self.list_git_files(self.directory)
        self.assertEqual(result,
                         set([os.path.realpath('héhé.html')]))

    def test_directory_symlink(self):
        import os
        import os.path
        os.mkdir(os.path.join(self.directory, 'subdir'))
        self.create_git_file('subdir', 'entry.txt')
        os.mkdir(os.path.join(self.directory, 'package'))
        self.create_git_file('package', 'root.txt')
        os.symlink(
                os.path.join(self.directory, 'subdir'),
                os.path.join(self.directory, 'package', 'data'))
        self.assertEqual(
                set(self.list_git_files(os.path.join(self.directory, 'package'))),
                set([os.path.realpath(os.path.join('subdir', 'entry.txt')),
                     os.path.realpath(os.path.join('package', 'root.txt'))]))

    def test_foreign_repo_symlink(self):
        import os
        import os.path
        import shutil
        os.mkdir(os.path.join(self.directory, 'subdir'))
        self.create_git_file('subdir', 'entry.txt')
        foreign = self.new_repo()
        try:
            os.mkdir(os.path.join(foreign, 'package'))
            self.create_git_file('package', 'root.txt')
            os.symlink(
                    os.path.join(self.directory, 'subdir'),
                    os.path.join(foreign, 'package', 'data'))
            self.assertEqual(
                    set(self.list_git_files(os.path.join(foreign, 'package'))),
                    set([os.path.realpath(os.path.join('package', 'root.txt'))]))
        finally:
            shutil.rmtree(foreign)


class gitlsfiles_tests(GitTestCase):

    def gitlsfiles(self, *a, **kw):
        from setuptools_git import gitlsfiles
        return gitlsfiles(*a, **kw)

    def test_empty_dirname(self):
        self.create_git_file('root.txt')
        self.assertEqual(
                set(self.gitlsfiles('')),
                set(['root.txt']))

    def test_specify_full_path(self):
        import os
        self.create_git_file('root.txt')
        os.chdir(self.old_cwd)
        self.assertEqual(
                set(self.gitlsfiles(self.directory)),
                set(['root.txt']))

    def test_package_root_in_repo_subdir(self):
        import os
        os.mkdir(os.path.join(self.directory, 'package'))
        self.create_git_file('package', 'root.txt')
        self.assertEqual(
                set(self.gitlsfiles(os.path.join(self.directory, 'package'))),
                set(['root.txt']))

    def test_directory_symlink(self):
        import os
        import os.path
        os.mkdir(os.path.join(self.directory, 'subdir'))
        self.create_git_file('subdir', 'entry.txt')
        os.mkdir(os.path.join(self.directory, 'package'))
        self.create_git_file('package', 'root.txt')
        os.symlink(
                os.path.join(self.directory, 'subdir'),
                os.path.join(self.directory, 'package', 'data'))
        self.assertEqual(
                set(self.gitlsfiles(os.path.join(self.directory, 'package'))),
                set(['root.txt',
                    os.path.join('data', 'entry.txt')]))

    def test_foreign_repo_symlink(self):
        import os
        import os.path
        import shutil
        os.mkdir(os.path.join(self.directory, 'subdir'))
        self.create_git_file('subdir', 'entry.txt')
        foreign = self.new_repo()
        try:
            os.mkdir(os.path.join(foreign, 'package'))
            self.create_git_file('package', 'root.txt')
            os.symlink(
                    os.path.join(self.directory, 'subdir'),
                    os.path.join(foreign, 'package', 'data'))
            self.assertEqual(
                    set(self.gitlsfiles(os.path.join(foreign, 'package'))),
                    set(['root.txt']))
        finally:
            shutil.rmtree(foreign)

