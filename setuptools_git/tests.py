import unittest

try:
    from subprocess import check_call
except ImportError:
    # BBB for python <2.5
    def check_call(*popenargs, **kwargs):
        from subprocess import call
        from subprocess import CalledProcessError
        retcode = call(*popenargs, **kwargs)
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        if retcode:
            raise CalledProcessError(retcode, cmd)
        return retcode


class GitTestCase(unittest.TestCase):
    def setUp(self):
        import os
        import tempfile
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
        import os.path
        fd = open(os.path.join(*path), 'wt')
        print >>fd, 'dummy'
        fd.close()

    def create_git_file(self, *path):
        import os.path
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

    def test_directory_symlink(self):
        import os
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
