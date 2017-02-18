from setuptools import setup, find_packages

version = '1.2'

setup(
    name="setuptools-git",
    version=version,
    maintainer='Marc Abramowitz',
    maintainer_email='msabramo@gmail.com',
    author="Yannick Gingras",
    author_email="ygingras@ygingras.net",
    url="https://github.com/wichert/setuptools-git",
    keywords='distutils setuptools git',
    description="Setuptools revision control system plugin for Git",
    long_description=open('README.rst').read(),
    license='BSD',
    packages=find_packages(),
    test_suite='setuptools_git',
    zip_safe=True,
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
        git=setuptools_git:listfiles

        [distutils.setup_keywords]
        use_vcs_version=setuptools_git:version_calc
        """
)
