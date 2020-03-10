import unittest
import os
from setuptools import setup

HERE = os.path.abspath(os.path.dirname(__file__))
README = os.path.join(HERE, "README.rst")

with open(README, 'r') as f:
    long_description = f.read()

setup(
    name='git_tools',
    version='0.1',
    description=('A collection of command-line utilities for interacting with '
                 'git repositories'),
    long_description=long_description,
    url='http://github.com/eriknyquist/git_tools',
    author='Erik Nyquist',
    author_email='eknyquist@gmail.com',
    license='Apache 2.0',
    packages=['git_tools'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'git-author-stats=git_tools.author_stats:main'
            'git-version-string=git_tools.version_string:main'
        ]
    }
)
