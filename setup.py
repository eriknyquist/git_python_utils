import unittest
import os
import sys
from setuptools import setup

package_name = "git_python_utils"

sys.path.insert(0, package_name)
import version

HERE = os.path.abspath(os.path.dirname(__file__))
README = os.path.join(HERE, "README.rst")
REQS = os.path.join(HERE, "requirements.txt")

with open(README, 'r') as fh:
    long_description = fh.read()

with open(REQS, 'r') as fh:
    requirements = fh.readlines()

version_str = version.version.strip()

setup(
    name=package_name,
    version=version_str,
    description=('A collection of command-line utilities for interacting with '
                 'git repositories'),
    long_description=long_description,
    url='http://github.com/eriknyquist/git_python_utils',
    author='Erik Nyquist',
    author_email='eknyquist@gmail.com',
    license='Apache 2.0',
    packages=['git_python_utils'],
    install_requires=requirements,
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'git-changelog=git_tools.changelog:main',
            'git-author-stats=git_tools.author_stats:main',
            'git-version-string=git_tools.version_string:main'
        ]
    }
)
