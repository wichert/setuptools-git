import sys
import os
import stat
import shutil
import unicodedata
import posixpath

if sys.version_info >= (3,):
    from urllib.parse import quote as url_quote
    unicode = str
else:
    from urllib import quote as url_quote

__all__ = ['check_call', 'check_output', 'b', 'fsdecode', 'posix',
           'rmtree', 'compose', 'decompose', 'hfs_quote']


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


try:
    from subprocess import check_output
except ImportError:
    # BBB for python <2.7
    def check_output(*popenargs, **kwargs):
        from subprocess import CalledProcessError
        from subprocess import PIPE
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
            raise CalledProcessError(retcode, cmd)
        return output


# Fake byte literals for Python <= 2.5
def b(s, encoding='utf-8'):
    if sys.version_info >= (3,):
        return s.encode(encoding)
    return s


# Decode path from fs encoding under Python 3
def fsdecode(path):
    if sys.version_info >= (3,):
        if not isinstance(path, str):
            return path.decode(sys.getfilesystemencoding(), 'surrogateescape')
    return path


# Convert path to POSIX path on Windows
def posix(path):
    if sys.platform == 'win32':
        return path.replace(os.sep, posixpath.sep)
    return path


# Windows cannot delete read-only Git objects
def rmtree(path):
    if sys.platform == 'win32':
        def onerror(func, path, excinfo):
            os.chmod(path, stat.S_IWRITE)
            func(path)
        shutil.rmtree(path, False, onerror)
    else:
        shutil.rmtree(path, False)


# HFS Plus uses decomposed UTF-8
def compose(path):
    if isinstance(path, unicode):
        return unicodedata.normalize('NFC', path)
    try:
        path = path.decode('utf-8')
        path = unicodedata.normalize('NFC', path)
        path = path.encode('utf-8')
    except UnicodeError:
        pass # Not UTF-8
    return path


# HFS Plus uses decomposed UTF-8
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

