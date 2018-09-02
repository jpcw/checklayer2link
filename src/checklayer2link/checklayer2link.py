#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Doc here.
"""

import argparse
from collections import namedtuple
import logging
import platform
import subprocess

import nagiosplugin

from nagiosplugin import Check
from nagiosplugin import CheckError
from nagiosplugin import Resource
from nagiosplugin import Metric
from nagiosplugin import ScalarContext
from nagiosplugin import Summary

__docformat__ = 'restructuredtext en'

_log = logging.getLogger('nagiosplugin')

platforms = {'OpenBSD': {'fields': ('Host', 'Mac', 'Netif', 'Expire'),
                         'wait': 'w'},
             'FreeBSD': {'fields': ('f0', 'Host', 'f2', 'Mac'),
                         'wait': 't'},
             'Linux': {'fields': ('f0', 'Host', 'f2', 'Mac'),
                       'wait': 'W'},
             }
system = platform.system()
options = platforms[system]


def _popen(cmd):  # pragma: no cover
    """Try catched subprocess.popen.

    raises explicit error
    """
    try:
        proc = subprocess.Popen(cmd,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        return stdout, stderr

    except OSError as e:
        message = "%s" % e
        raise CheckError(message)


def _ping(ip, wait=1, count=1, resolve=False):
    """Check if an ip is pinguable."""

    _cmd = ['ping', '-%s %s' % (options['wait'], wait)]

    if not resolve:
        _cmd.append('-n')
    _cmd.append('-c %s' % count)
    _cmd.append('%s' % ip)

    subprocess.call(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


class CheckLayer2Link(Resource):
    """Check bgpctl sessions plugin."""

    def __init__(self, ip, maxwait=1, count=1):
        self.ip = ip
        self.maxwait = maxwait
        self.count = count

    def _find_ip_arp_table(self, system=system):
        """Runs 'bgpctl show'."""
        _cmd = "arp -na"
        _log.debug("running '%s'", _cmd)
        result = 0
        stdout, stderr = _popen(_cmd.split())

        if not isinstance(stderr, str):  # pragma: no cover
            stderr = stderr.decode()
        if not isinstance(stdout, str):  # pragma: no cover
            stdout = stdout.decode()

        if stderr:
            message = "%s" % (stderr.splitlines()[-1])
            _log.info(message)
            raise CheckError(message)

        if stdout:
            if system == 'OpenBSD':
                output = stdout.splitlines()[1:]
            else:
                output = stdout.splitlines()
            if output:
                ArpEntry = namedtuple('ArpEntry', platforms[system]['fields'])
                for line in output:
                    data = line.split()[0:4]
                    entry = ArpEntry(*data)
                    ip = entry.Host
                    if system in ('Linux', 'FreeBSD'):
                        # here we remove () around ip
                        ip = ip[1:-1]
                    if ip == self.ip:
                        if len(entry.Mac.split(':')) == 6:
                            result = 1
                            break

                return result

    def probe(self, system=system):
        """."""
        _ping(self.ip, self.maxwait, self.count)

        return Metric('mac', self._find_ip_arp_table(system), context='arp')


class AuditSummary(Summary):
    """Status line conveying informations."""

    def ok(self, results):
        """Summarize OK(s)."""
        ip = results.by_name['mac'].resource.ip
        return 'layer 2 for ip %s is up' % ip

    def problem(self, results):
        """Summarize CRITICAL(s)."""
        ip = results.by_name['mac'].resource.ip
        return 'layer 2 for ip %s is down' % ip


def parse_args():  # pragma: no cover
    """Arguments parser."""
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument('ip', help='ip to find in arp table')
    argp.add_argument('-v', '--verbose', action='count', default=0,
                      help='increase output verbosity (use up to 3 times)')
    argp.add_argument('-w', '--maxwait', type=int, default=1,
                      help="default = 1, man ping")
    argp.add_argument('-c', '--count', type=int, default=1,
                      help="default = 1, man ping")

    return argp.parse_args()


@nagiosplugin.guarded
def main():  # pragma: no cover

    args = parse_args()
    check = Check(CheckLayer2Link(args.ip, args.maxwait, args.count),
                  ScalarContext('arp', None, '1:1'),
                  AuditSummary())
    check.main(args.verbose)


if __name__ == '__main__':  # pragma: no cover
    main()

# vim:set et sts=4 ts=4 tw=80:
