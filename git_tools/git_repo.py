import time
import os
from git import Repo

from git_tools.author import RepoAuthor

default_fmt = [".", "tag", "commits", "-", "dirty", "incsha"]


class VersionInfo(object):
    dirty_tag = "dirty"
    literal_char = "%"

    def __init__(self, tag, branch, commits_since, is_dirty, sha, working_dir):
        self.tag = tag
        self.branch = branch
        self.commits = commits_since
        self.is_dirty = is_dirty
        self.sha = sha
        self.dir = working_dir

        self.sep = "."

        self._fmt_args = {
            "tag": lambda x: x.tag,
            "commits": lambda x: str(x.commits),
            "inccommits": lambda x: str(x.commits) if x.commits else None,
            "dirty": lambda x: x.__class__.dirty_tag if x.is_dirty else None,
            "sha": lambda x: x.sha,
            "incsha": lambda x: x.sha if not x.tag else None,
            "branch": lambda x: x.branch,
            "dir": lambda x: x.dir,
            "timestamp": lambda x: str(int(time.time())),
            "datetime": lambda x: time.strftime("%Y%m%d-%H%M%S", time.gmtime())
        }

    def format(self, fmt):
        ret = ""

        for i in range(len(fmt)):
            tok = fmt[i].strip()

            if (len(tok) > 0) and (tok[0] == self.__class__.literal_char):
                field = tok[1:]
            else:
                if tok not in self._fmt_args:
                    # New separator set
                    self.sep = tok
                    continue

                field = self._fmt_args[tok](self)
                if not field:
                    continue

            if ret:
                ret += self.sep

            ret += field

        return ret

class GitRepo(Repo):
    def __init__(self, *args, **kwargs):
        super(GitRepo, self).__init__(*args, **kwargs)
        self._authors = {}
        self._ignore_authors = ['Not Committed Yet']

    def file_list(self):
        return [e[0] for e in self.index.entries]

    def _repo_author_info(self, file_whitelist, file_blacklist):
        _authors = {}
        for fn in self.file_list():

            ext = os.path.splitext(fn)[1]
            if file_whitelist and (ext not in file_whitelist):
                continue

            if file_blacklist and (ext in file_blacklist):
                continue

            blame_results = self.blame(None, fn)
            for result in blame_results:
                commit, lines = result
                name = str(commit.author)

                if name in self._ignore_authors:
                    continue

                if name not in _authors:
                    _authors[name] = RepoAuthor(name)

                _authors[name].line_count += len(lines)


                if commit.hexsha not in _authors[name].commits:
                    _authors[name].commits[commit.hexsha] = commit
                    _authors[name].commit_count += 1

                if ((not _authors[name].latest_commit) or
                    (_authors[name].latest_commit.committed_date < commit.committed_date)):
                    _authors[name].latest_commit = commit

        return _authors

    def author_stats(self, author_whitelist=[], author_blacklist=[],
                     file_whitelist=[], file_blacklist=[]):
        authors = self._repo_author_info(file_whitelist, file_blacklist)
        if author_blacklist:
            return [authors[a] for a in authors if a not in blacklist]

        if author_whitelist:
            return [authors[a] for a in authors if a in whitelist]

        return list(authors.values())

    def _latest_tag_info(self):
        taghashes = {t.commit.hexsha: t for t in self.tags}

        commits_since = 0
        for commit in self.iter_commits(None):
            if commit.hexsha in taghashes:
                tag = taghashes[commit.hexsha]
                return tag.name, commits_since

            commits_since += 1

        return None, commits_since

    def generate_version_string(self, fmt=default_fmt, dirty_tag="dirty",
                                literal_char="%"):
        VersionInfo.dirty_tag = dirty_tag
        VersionInfo.literal_char = literal_char

        tagname, commits_since = self._latest_tag_info()
        if tagname is None:
            tagname = "v0.0.1"

        return VersionInfo(tagname, self.active_branch.name, commits_since,
                           self.is_dirty(), self.head.commit.hexsha[:8],
                           os.path.basename(self.working_dir)).format(fmt)
