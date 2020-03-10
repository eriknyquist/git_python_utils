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

    def _latest_tag_info(self):
        taghashes = {t.commit.hexsha: t for t in self.tags}

        commits_since = 0
        for commit in self.iter_commits(None):
            if commit.hexsha in taghashes:
                tag = taghashes[commit.hexsha]
                return tag.name, commits_since

            commits_since += 1

        return None, commits_since

    def generate_version_string(self):
        tagname, commits_since = self._latest_tag_info()
        if tagname is None:
            ret = "v0.0.1"
        else:
            ret = tagname

        if (tagname is not None) and (commits_since > 0):
            ret += ".%d" % commits_since

        if self.is_dirty():
            ret += "-dev"

        if tagname is None:
            ret += "-%s" % (self.head.commit.hexsha[:8])

        return ret
