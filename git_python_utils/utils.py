import os

from git_python_utils.git_repo import GitRepo


def open_git_repo(path):
    if not os.path.isdir(path):
        print("Error accessing repo at path %s: no such directory" % path)
        return None

    try:
        ret = GitRepo(path)
    except Exception as e:
        print("Error accessing repo at path %s: %s" % (path, str(e)))
        return None

    return ret
