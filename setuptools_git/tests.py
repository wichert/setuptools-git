import unittest


class is_child_tests(unittest.TestCase):
    def is_child(self, *a, **kw):
        from setuptools_git import is_child
        return is_child(*a, **kw)

    def test_same_directory(self):
        self.assertEqual(self.is_child('one', 'one'), False)

    def test_subdir(self):
        import os
        self.assertEqual(
                self.is_child('foo', os.path.join('foo', 'bar')),
                True)

    def test_parent(self):
        import os
        self.assertEqual(
                self.is_child(os.path.join('foo', 'bar'), 'foo'),
                False)

    def test_prefix(self):
        import os
        self.assertEqual(
                self.is_child('foo', os.path.join('foo1', 'bar')),
                False)


class GitTestCase(unittest.TestCase):
    def setUp(self):
        import os
        import tempfile
        from setuptools_git.compat import check_call
        self.directory = tempfile.mkdtemp()
        self.old_cwd = os.getcwd()
        os.chdir(self.directory)
        check_call(['git', 'init', '--quiet', self.directory])

    def tearDown(self):
        import os
        import shutil
        shutil.rmtree(self.directory)
        os.chdir(self.old_cwd)

    def create_file(self, *path):
        import os
        fd = open(os.path.join(*path), 'wt')
        print >>fd, 'dummy'
        fd.close()

    def create_git_file(self, *path):
        import os
        from setuptools_git.compat import check_call
        filename = os.path.join(*path)
        fd = open(filename, 'wt')
        print >>fd, 'dummy'
        fd.close()
        check_call(['git', 'add', filename])
        check_call(['git', 'commit', '--quiet', '-m', 'add new file'])

    def create_git_symlink(self, source, target):
        import os
        from setuptools_git.compat import check_call
        os.symlink(source, target)
        check_call(['git', 'add', target])
        check_call(['git', 'commit', '--quiet', '-m', 'add new symlink'])


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

    def test_at_repo_subdir(self):
        import os
        import os.path
        self.create_git_file('root.txt')
        os.mkdir(os.path.join(self.directory, 'subdir'))
        self.create_git_file('subdir', 'entry.txt')
        self.assertEqual(
                self.list_git_files(self.directory),
                set([os.path.realpath('root.txt'),
                     os.path.realpath(os.path.join('subdir', 'entry.txt'))]))


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

    def test_directory_outside_package_symlinked(self):
        import os
        os.mkdir(os.path.join(self.directory, 'subdir'))
        self.create_git_file('subdir', 'entry.txt')
        os.mkdir(os.path.join(self.directory, 'package'))
        self.create_git_file('package', 'root.txt')
        self.create_git_symlink(
                os.path.join('..', 'subdir'),
                os.path.join('package', 'data'))
        self.assertEqual(
                set(self.gitlsfiles(os.path.join(self.directory, 'package'))),
                set(['root.txt',
                    os.path.join('data', 'entry.txt')]))

    def test_no_symlink_duplicates(self):
        import os
        os.mkdir(os.path.join(self.directory, 'subdir1'))
        self.create_git_file('subdir1', 'entry.txt')
        self.create_git_symlink('subdir1', 'subdir2')
        self.assertEqual(
                set(self.gitlsfiles(self.directory)),
                set([os.path.join('subdir1', 'entry.txt'),
                     'subdir2']))
