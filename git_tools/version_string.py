import sys
from argparse import ArgumentParser

from git_tools.utils import open_git_repo


def main():
    parser = ArgumentParser(description='Print a version')
    parser.add_argument('-d', '--directory', dest='directory', default='.',
            help="Path to git repo directory")
    args = parser.parse_args()

    r = open_git_repo(args.directory)
    if r is None:
        return -1

    print(r.generate_version_string())
    return 0

if __name__ == "__main__":
    sys.exit(main())
