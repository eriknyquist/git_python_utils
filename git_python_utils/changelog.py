import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from git_python_utils.utils import open_git_repo
from git_python_utils.git_repo import datetime_fmts

desc = 'Print a changelog for a range of commits'
epilog = ('''

Date/time Format
----------------

The following formats are accepted by the --start-date and --end-date options:

%s
''' % '\n'.join([f[1] for f in datetime_fmts]))


def main():
    parser = ArgumentParser(description=desc,
                            formatter_class=RawDescriptionHelpFormatter,
                            epilog=epilog)

    parser.add_argument('-d', '--directory', dest='directory', default='.',
            help="Path to git repo directory")
    parser.add_argument('-T', '--start-tag', dest='start_tag', default=None,
            help="Earliest tag in range")
    parser.add_argument('-t', '--end-tag', dest='end_tag', default=None,
            help="Latest tag in range")
    parser.add_argument('-S', '--start-date', dest='start_date', default=None,
            help="Earliest date in range")
    parser.add_argument('-s', '--end-date', dest='end_date', default=None,
            help="Latest date in range")
    parser.add_argument('-C', '--start-commit', dest='start_commit', default=None,
            help="Earliest commit SHA in range")
    parser.add_argument('-c', '--end-commit', dest='end_commit', default=None,
            help="Latest commit SHA in range")
    args = parser.parse_args()

    r = open_git_repo(args.directory)
    if r is None:
        return -1

    try:
        log = r.changelog(args.start_tag, args.end_tag, args.start_date,
                          args.end_date, args.start_commit, args.end_commit)
    except RuntimeError as e:
        print("Error: %s" % e)
        return -1

    print(log)
    return 0

if __name__ == "__main__":
    sys.exit(main())
