import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from git_tools.utils import open_git_repo
from git_tools.git_repo import datetime_fmts

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
    parser.add_argument('-s', '--start-tag', dest='start_tag', default=None,
            help="Earliest tag in range")
    parser.add_argument('-e', '--end-tag', dest='end_tag', default=None,
            help="Latest tag in range")
    parser.add_argument('-S', '--start-date', dest='start_date', default=None,
            help="Earliest date in range")
    parser.add_argument('-E', '--end-date', dest='end_date', default=None,
            help="Latest date in range")
    args = parser.parse_args()

    r = open_git_repo(args.directory)
    if r is None:
        return -1

    try:
        log = r.changelog(args.start_tag, args.end_tag, args.start_date, args.end_date)
    except RuntimeError as e:
        print("Error: %s" % e)
        return -1

    print(log)
    return 0

if __name__ == "__main__":
    sys.exit(main())
