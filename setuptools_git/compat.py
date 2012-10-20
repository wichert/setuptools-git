import sys

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


# If path is Unicode, encode to filesystem encoding
def fsencode(path):
    if sys.version_info >= (3,):
        if isinstance(path, str):
            return path.encode(sys.getfilesystemencoding(), 'surrogateescape')
    return path


# Python 3 compatibility
if sys.version_info >= (3,):
    from urllib.parse import quote as url_quote
else:
    from urllib import quote as url_quote


__all__ = ['check_call', 'check_output', 'b', 'fsencode', 'url_quote']
