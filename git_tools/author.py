import time


class RepoAuthor(object):
    def __init__(self, name):
        self.name = name
        self.commit_count = 0
        self.line_count = 0
        self.latest_commit = None
        self.commits = {}

    def __str__(self):
        commit_time = self.latest_commit.committed_date - self.latest_commit.committer_tz_offset
        ret = ["%s:" % self.name]
        ret.append("  commit count: %d" % self.commit_count)
        ret.append("  line count: %d" % self.line_count)
        ret.append("  last commit: %s (%s)" %
                   (time.strftime("%d %B %Y, %H:%M:%S", time.gmtime(commit_time)),
                       self.latest_commit.hexsha[:8]))
        return '\n'.join(ret)
