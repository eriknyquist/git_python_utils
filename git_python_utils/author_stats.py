import sys
from argparse import ArgumentParser

from git_python_utils.utils import open_git_repo


def main():
    parser = ArgumentParser(description='Print statistics about commit authors')
    parser.add_argument('-d', '--directory', dest='directory', default='.',
            help="Path to git repo directory")
    parser.add_argument('-a', '--author-whitelist', dest='author_wlist', default='',
            help="Whitelist of author names. Filters results to only authors in"
                 " the given comma-separated list.")
    parser.add_argument('-A', '--author-blacklist', dest='author_blist', default='',
            help="Blacklist of author names. Filters results to only authors not"
                 " in the given comma-separated list.")
    parser.add_argument('-f', '--file-whitelist', dest='ftype_wlist', default='',
            help="Whitelist of filename extensions. Filters files to only types "
                 " in the given comma-separated list.")
    parser.add_argument('-F', '--file-blacklist', dest='ftype_blist', default='',
            help="Blacklist of filename extensions. Filters files to only types "
                 " not in the given comma-separated list.")
    args = parser.parse_args()

    awhitelist = args.author_wlist.split(',') if args.author_wlist else []
    ablacklist = args.author_blist.split(',') if args.author_blist else []
    fwhitelist = args.ftype_wlist.split(',') if args.ftype_wlist else []
    fblacklist = args.ftype_blist.split(',') if args.ftype_blist else []

    r = open_git_repo(args.directory)
    if r is None:
        return -1

    authors = r.author_stats(awhitelist, ablacklist, fwhitelist, fblacklist)
    print()
    for a in authors:
        print(str(a) + "\n")

    return 0

if __name__ == "__main__":
    sys.exit(main())
