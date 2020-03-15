import datetime
import time
import os
from git import Repo
from datetime import datetime, timedelta

from git_tools.author import RepoAuthor

default_version_fmt = [".", "tag", "commits", "-", "dirty", "incsha"]

datetime_fmts = [
    ('%Y/%m/%d', 'YYYY/MM/DD'),
    ('%Y-%m-%d', 'YYYY-MM-DD'),
    ('%Y/%m/%d %H:M', 'YYYY/MM/DD HH:MM'),
    ('%Y-%m-%d_%H-M', 'YYYY-MM-DD_HH-MM')
]


class VersionInfo(object):
    dirty_tag = "dirty"
    literal_char = "%"

    def __init__(self, repo, tag, branch, commits_since, is_dirty,
                 sha, working_dir):
        self.repo = repo
        self.tag = tag
        self.branch = branch
        self.commits = commits_since
        self.is_dirty = is_dirty
        self.sha = sha
        self.dir = working_dir

        self.sep = "."

        self._fmt_args = {
            "tag": lambda x: x.tag,
            "since": lambda x: str(x.commits),
            "nsince": lambda x: str(x.commits) if x.commits else None,
            "commits": lambda x: str(x.repo.git.rev_list('--count', 'HEAD')),
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


class ChangeLogCommitInfo(object):
    def __init__(self, commit):
        self.utc_seconds = commit.committed_date
        self.utc_offset = commit.committer_tz_offset
        self.sha = commit.hexsha
        self.author = commit.author
        self.message = commit.message

    def commit_day(self):
        return datetime.fromtimestamp(self.utc_seconds).strftime("%d %b %Y")

    def __str__(self):
        return "%s  %s" % (self.sha[:8], self.message.split("\n")[0])

    def __repr__(self):
        return self.__str__()


class ChangeLog(object):
    def __init__(self):
        self.commits = []

    def add_commit(self, commit):
        self.commits.append(ChangeLogCommitInfo(commit))

    def __str__(self):
        ret = []
        date = None

        for c in self.commits:
            commit_day = c.commit_day()
            if commit_day != date:
                date = commit_day
                ret.append("")
                ret.append("# Commits on %s" % date)

            ret.append(str(c))

        return '\n'.join(ret).strip()

    def __repr__(self):
        return self.__str__()


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

    def generate_version_string(self, fmt=default_version_fmt, dirty_tag="dirty",
                                literal_char="%"):
        VersionInfo.dirty_tag = dirty_tag
        VersionInfo.literal_char = literal_char

        tagname, commits_since = self._latest_tag_info()
        if tagname is None:
            tagname = "v0.0.1"

        v = VersionInfo(self, tagname, self.active_branch.name, commits_since,
                        self.is_dirty(), self.head.commit.hexsha[:8],
                        os.path.basename(self.working_dir))

        return v.format(fmt)

    def _parse_datetime(self, datestr):
        parsed = None

        for fmt, _ in datetime_fmts:
            try:
                dt = datetime.strptime(datestr, fmt)
            except ValueError:
                pass
            else:
                parsed = dt
                break

        # Convert naive DT object to seconds since UNIX epoch
        return int((parsed - datetime(1970, 1, 1)) / timedelta(seconds=1))

    def _iter_commits_in_date_range(self, start_date, end_date):
        start_secs = self._parse_datetime(start_date)
        end_secs = self._parse_datetime(end_date)

        seen_end = False
        for commit in self.iter_commits(None):
            if commit.committed_date <= end_secs:
                seen_end = True

            if commit.committed_date <= start_secs:
                break

            yield commit

    def _iter_commits_in_tag_range(self, start_tag, end_tag):
        tagnames = {t.name: t for t in self.tags}
        taghashes = {t.commit.hexsha: t for t in self.tags}
        end_sha = None
        start_sha = None

        if (start_tag is not None) and (start_tag not in tagnames):
            raise RuntimeError("tag '%s' not found in repo %s" %
                               (start_tag, os.path.basename(self.working_dir)))

        if (end_tag is not None) and (end_tag not in tagnames):
            raise RuntimeError("tag '%s' not found in repo %s" %
                               (end_tag, os.path.basename(self.working_dir)))

        if end_tag is None:
            # Use HEAD as end SHA if no end tag is set
            end_sha = self.head.commit.hexsha
        else:
            # Otherwise, grab the commit SHA of the given tag
            end_sha = tagnames[end_tag].commit.hexsha

        if start_tag is not None:
            start_sha = tagnames[start_tag].commit.hexsha

        seen_end = False
        for commit in self.iter_commits(None):
            if commit.hexsha == end_sha:
                seen_end = True

            if start_sha is None:
                # If no start tag is defined, we should stop at the first tag
                # we see after end commit SHA
                if (commit.hexsha in taghashes) and (commit.hexsha != end_sha):
                    break

            elif start_sha == commit.hexsha:
                # Otherwise, stop at the defined start tag
                break

            if seen_end:
                yield commit

    def changelog(self, start_tag=None, end_tag=None, start_date=None, end_date=None):
        changelog = ChangeLog()

        if None not in [start_date, end_date]:
            for commit in self._iter_commits_in_date_range(start_date, end_date):
                changelog.add_commit(commit)

        else:
            for commit in self._iter_commits_in_tag_range(start_tag, end_tag):
                changelog.add_commit(commit)

        return changelog
