import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from git_python_utils.utils import open_git_repo
from git_python_utils.git_repo import default_version_fmt

default_fmt_str = ",".join(default_version_fmt)

desc='Print a formatted version string based on git history'
epilog=('''

Format Tokens
-------------

Version string format is described using a comma-seperated list of strings,
representing an ordered list of formatting instructions. Version strings are
typically divided into sections with some seperation character, so most
formatting instructions describe a value to placed into a single field within the
version string. Each formatting instruction falls into one of two categories:

    *  A built-in keyword representing a value to be inserted into the current
       field of the version string. Inserts the value and increments the field
       counter to point at the next field (order of fields in the version string
       matches the order of built-in keywords in the input format list)

    * A seperator definition.

Any string in the list of provided format tokens that does not match a built-in
keyword will be treated as a seperator definition, and that string will be used
to separate further fields in the version string until another separator
definition is seen. The default separator is ".".

Available built-in keywords
---------------------------

    * tag          : Produces the name of the most recent tag on the active branch.
                     "v0.0.1" is used if no tags are present on the active branch.

    * since        : Produces the number of commits since the most recent tag.
                     Produces the total number of commits if no tags are
                     present on the active branch.

    * nsince       : Produces the number of commits since the most recent tag.
                     Produces the total number of commits if no tags are
                     present on the active branch. Produces no output in the version
                     string if the resulting commit count is 0.

    * commits      : Produces the total number of commits on the active branch

    * dirty        : Produces the defined dirty tag (default is "dirty") if the
                     repo is dirty, otherwise produces no output in the version
                     string.

    * sha          : Produces the first 8 hex characters of the latest commit
                     SHA in the repo.

    * incsha       : Produces the first 8 hex characters of the latest commit
                     SHA in the repo. Produces no output in the version string
                     if tags are present in the active branch.

    * branch       : Produces the active branch name.

    * dir          : Produces the repo's root directory name.

    * timestamp    : Produces a timestamp in seconds since  the UNIX epoch

    * datetime     : Produces a human-readable date/time in "YYYYMMDD-HHMMSS"
                     format

    * %            : Indicates the remaining characters in the format token
                     should be copied as-is into the version string. Use this
                     to insert literal strings into the version string, e.g.
                     "%mystring" would insert the characters "mystring" into the
                     current field of the version string.
Example
-------

Consider the following list of format tokens:

_,tag,commits,branch,+,sha,%testing

This would generate a version string in the following format:

<tag>_<commits>_<branch>+<sha>+testing
\n 
''')

def main():
    parser = ArgumentParser(description=desc,
                            formatter_class=RawDescriptionHelpFormatter,
                            epilog=epilog)

    parser.add_argument('-r', '--repo-directory', dest='directory', default='.',
            help="Path to git repo directory (default=%(default)s)")
    parser.add_argument('-d', '--dirty-tag', dest='dirty_tag', default='dirty',
            help="Tag used to indicate repo is dirty for 'dirty' keyword "
            "(default=%(default)s)")
    parser.add_argument('-l', '--literal-char', dest='literal_char', default='%',
            help="Character used to indicate a literal string (default=%(default)s)")
    parser.add_argument('-p', '--pip-friendly', action='store_true',
            dest='pipfriendly', default=False,
            help="Generate version string suitable for pip-installable packages "
            "(default=%(default)s)")
    parser.add_argument('-f', '--format', dest='fmt', default=default_fmt_str,
            help="Comma-separated sequence of tokens to describe version string "
            "format (see 'Format Tokens' section) (default=%(default)s)")
    parser.add_argument('-t', '--template', dest='template_file', default=None,
            help="Path to template file (overrides '-f' option)")
    parser.add_argument('-o', '--output', dest='output_file', default=None,
            help="Output to file instead of stdout")

    args = parser.parse_args()

    r = open_git_repo(args.directory)
    if r is None:
        return -1

    if args.template_file is None:
        fmt_args = [x.strip() for x in args.fmt.split(",")]
        ver = r.generate_version_string(fmt=fmt_args, dirty_tag=args.dirty_tag,
                                        literal_char=args.literal_char,
                                        pipfriendly=args.pipfriendly)

    else:
        ver = r.process_template(args.template_file)

    if args.output_file is None:
        print(ver)
    else:
        with open(args.output_file, 'w') as fh:
            fh.write(ver)

    return 0

if __name__ == "__main__":
    sys.exit(main())
