import sys
from git_python_utils.git_repo import GitRepo

def main():
    if len(sys.argv) != 2:
        print("Usage: %s <output_filename>" % __file__)
        return -1

    r = GitRepo('.')
    ver = r.generate_version_string()

    with open(sys.argv[1], 'w') as fh:
        fh.write("version = \"%s\"\n" % ver)

    return 0

if __name__ == "__main__":
    main()
