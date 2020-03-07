from argparse import ArgumentParser

from git_tools.git_repo import GitRepo


def main():
    parser = ArgumentParser(description='Print statistics about commit authors')
    parser.add_argument('-d', '--directory', dest='directory', default='.',
            help="Path to git repo directory")
    parser.add_argument('-w', '--whitelist', dest='whitelist', default='',
            help="Whitelist of author names. Filters results to only authors in"
                 " the given comma-separated list.")
    parser.add_argument('-b', '--blacklist', dest='blacklist', default='',
            help="Blacklist of author names. Filters results to only authors not"
                 " in the given comma-separated list.")
    args = parser.parse_args()

    whitelist = args.whitelist.split(',') if args.whitelist else []
    blacklist = args.blacklist.split(',') if args.blacklist else []

    r = GitRepo(args.directory)
    authors = r.author_stats(whitelist, blacklist)

    print()
    for a in authors:
        print(str(a) + "\n")

if __name__ == "__main__":
    main()
