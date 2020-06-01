Command-line Git utilities written in Python
--------------------------------------------

Install from pypi:

::

    python -m pip install git_python_utils

git_python_tools.version_string
===============================

Automatic version string generation based on git history. Customizable version string
format using a format string or a template file.

Run with -h for usage information:

::

    python -m git_python_utils.version_string -h

git_python_tools.author_stats
=============================

Prints information about each author in the git history (number of commits,
number of lines, latest commit).

Run with -h for usage information:

::

    python -m git_python_utils.author_stats -h

git_python_tools.changelog
==========================

Prints a CHANGELOG style list of commits between a particular range, grouped
by commit date. By default, will include commits between the most recent tag and
HEAD.

Run with -h for usage information:

::

    python -m git_python_utils.changelog -h

