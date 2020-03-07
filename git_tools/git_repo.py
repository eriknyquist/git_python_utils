import os
from git import Repo

from git_tools.author import RepoAuthor


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
