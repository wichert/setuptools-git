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


class Base(unittest.TestCase):
    def setUp(self):
        import os
        import tempfile
        self.directory=tempfile.mkdtemp()
        self.old_cwd=os.getcwd()
        os.chdir(self.directory)

    def tearDown(self):
        import os
        import shutil
        shutil.rmtree(self.directory)
        os.chdir(self.old_cwd)

    def create_file(self, *path):
        import os.path
        fd=open(os.path.join(*path), 'wt')
        print >>fd, 'dummy'
        fd.close()

    def create_git_file(self, *path):
        import os.path
        filename=os.path.join(*path)
        fd=open(filename, 'wt')
        print >>fd, 'dummy'
        fd.close()
        check_call(['git', 'add', filename])
        check_call(['git', 'commit', '-m', 'add new file'])


class list_git_files_tests(Base):
    def list_git_files(self, *a, **kw):
        from setuptools_git import list_git_files
        return list_git_files(*a, **kw)

    def test_at_repo_root(self):
        import os.path
        check_call(['git', 'init', self.directory])
        self.create_git_file('root.txt')
        self.assertEqual(
                self.list_git_files(self.directory),
                set([os.path.realpath('root.txt')]))

    def test_at_repo_subdir(self):
        import os
        import os.path
        check_call(['git', 'init', self.directory])
        self.create_git_file('root.txt')
        os.mkdir(os.path.join(self.directory, 'subdir'))
        self.create_git_file('subdir', 'entry.txt')
        self.assertEqual(
                self.list_git_files(self.directory),
                set([os.path.realpath('root.txt'),
                     os.path.realpath(os.path.join('subdir', 'entry.txt'))]))

