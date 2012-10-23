import sys

try:
    from setuptools import setup
except ImportError:
    try:
        from ez_setup import use_setuptools
    except ImportError:
        print("can't find ez_setup")
        print("try: wget http://peak.telecommunity.com/dist/ez_setup.py")
        sys.exit(1)
    use_setuptools()
    from setuptools import setup


version = '1.0b1dev'

setup(
    name="setuptools-git",
    version=version,
    author="Yannick Gingras",
    author_email="ygingras@ygingras.net",
    url="https://github.com/wichert/setuptools-git",
    keywords='distutils setuptools git',
    description="Setuptools revision control system plugin for Git",
    long_description=open('README.rst').read(),
    license='BSD',
    test_suite='setuptools_git',
    classifiers=[
        "Topic :: Software Development :: Version Control",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.4",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        ],
    entry_points="""
        [setuptools.file_finders]
        git=setuptools_git:gitlsfiles
        """
)
