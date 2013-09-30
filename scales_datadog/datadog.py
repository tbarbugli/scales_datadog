"""Tools for pushing stat values to datadog."""

from greplin import scales
import os
import threading
import logging
import time
from ssl import SSLError
from fnmatch import fnmatch
import datetime


class DataDogPusher(object):

    """A class that pushes all stat values to DataDog on-demand."""

    def __init__(self, api_key, api_application_key):
        """If prefix is given, it will be prepended to all Graphite
        stats. If it is not given, then a prefix will be derived from the
        hostname."""
        from dogapi import dog_http_api
        self.api = dog_http_api
        self.rules = []
        self.pruneRules = []
        self.api.api_key = api_key
        self.api.api_application_key = api_application_key

    def _sanitize(self, name):
        """Sanitize a name for datadog."""
        return name.strip().replace(' ', '-').replace('/', '_')

    def _forbidden(self, path, value):
        """Is a stat forbidden? Goes through the rules to find one that
        applies. Chronologically newer rules are higher-precedence than
        older ones. If no rule applies, the stat is forbidden by default."""
        if path[0] == '/':
            path = path[1:]
        for rule in reversed(self.rules):
            if isinstance(rule[1], basestring):
                if fnmatch(path, rule[1]):
                    return not rule[0]
            elif rule[1](path, value):
                return not rule[0]
        return True  # do not log by default

    def _pruned(self, path):
        """Is a stat tree node pruned?  Goes through the list of prune rules
        to find one that applies.  Chronologically newer rules are
        higher-precedence than older ones. If no rule applies, the stat is
        not pruned by default."""
        if path[0] == '/':
            path = path[1:]
        for rule in reversed(self.pruneRules):
            if isinstance(rule, basestring):
                if fnmatch(path, rule):
                    return True
            elif rule(path):
                return True
        return False  # Do not prune by default

    def make_metrics(self, statsDict, prefix, path):
        """ returns a dict with metric / values """
        d = datetime.datetime.now()
        now = int(time.mktime(d.timetuple()))
        metrics = []
        if statsDict is None:
            statsDict = scales.getStats()
        prefix = prefix or ''
        path = path or '/'
        for name, value in statsDict.items():
            name = str(name)
            subpath = os.path.join(path, name)

            if self._pruned(subpath):
                continue

            if hasattr(value, '__call__'):
                try:
                    value = value()
                except Exception:
                    value = None
                    logging.exception(
                        'Error when calling stat function for push')

            if hasattr(value, 'iteritems'):
                metrics += self.make_metrics(value, '%s%s.' %
                          (prefix, self._sanitize(name)), subpath)
            elif self._forbidden(subpath, value):
                continue
            elif type(value) in (int, long, float) and len(name) < 500:
                metrics.append({'metric': prefix + self._sanitize(name), 'points': [(now, value)]})
        return metrics

    def push(self, statsDict=None, prefix=None, path=None):
        """Push stat values to DataDog."""
        metrics = self.make_metrics(statsDict, prefix, path)
        print 'push %r' % metrics
        self.api.metrics(metrics)

    def _addRule(self, isWhitelist, rule):
        """Add an (isWhitelist, rule) pair to the rule list."""
        if isinstance(rule, basestring) or hasattr(rule, '__call__'):
            self.rules.append((isWhitelist, rule))
        else:
            raise TypeError(
                'Graphite logging rules must be glob pattern or callable. Invalid: %r' % rule)

    def allow(self, rule):
        """Append a whitelisting rule to the chain. The rule is either a function (called
        with the stat name and its value, returns True if it matches), or a Bash-style
        wildcard pattern, such as 'foo.*.bar'."""
        self._addRule(True, rule)

    def forbid(self, rule):
        """Append a blacklisting rule to the chain. The rule is either a function (called
        with the stat name and its value, returns True if it matches), or a Bash-style
        wildcard pattern, such as 'foo.*.bar'."""
        self._addRule(False, rule)

    def prune(self, rule):
        """Append a rule that stops traversal at a branch node."""
        self.pruneRules.append(rule)


class DataDogPeriodicPusher(threading.Thread, DataDogPusher):

    """A thread that periodically pushes all stat values to DataDog."""

    def __init__(self, api_key, api_application_key, period=60):
        DataDogPusher.__init__(self, api_key, api_application_key)
        threading.Thread.__init__(self)
        self.daemon = True
        self.period = period

    def run(self):
        """Loop forever, pushing out stats."""
        while True:
            logging.info(
                'DataDog pusher is sleeping for %d seconds', self.period)
            time.sleep(self.period)
            logging.info('Pushing stats to DataDog')
            try:
                self.push()
                logging.info('Done pushing stats to DataDog')
            except SSLError:
                logging.exception("Connection issue with datadog")
            except Exception:
                logging.exception('Exception while pushing stats to DataDog')
                raise
