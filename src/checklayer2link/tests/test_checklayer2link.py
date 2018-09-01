
import mock

try:
    import unittest2 as unittest
except ImportError:  # pragma: no cover
    import unittest

import nagiosplugin
from nagiosplugin import CheckError

from checklayer2link import checklayer2link

freebsd_arp_na_output_without_ip = \
    '? (10.61.0.20) at f4:8c:50:07:62:d7 on wlan0 permanent [ethernet]\n'\
    '? (10.61.0.1) at 00:0d:b4:07:86:fb on wlan0 expires  [ethernet]'

freebsd_arp_na_output_with_ip = \
    '? (10.61.0.20) at f4:8c:50:07:62:d7 on wlan0 permanent [ethernet]\n'\
    '? (10.61.0.254) at 00:0d:b4:07:86:fb on wlan0 expires  [ethernet]'

openbsd_arp_na_output_with_ip = \
    'Host                     Ethernet Address   Netif Expire     Flags\n'\
    '10.61.0.254              00:30:88:02:0e:0d  carp1 8m38s      \n'\
    '85.14.151.86             00:00:5e:00:01:05  carp5 permanent  l\n'\
    '91.226.28.0              (incomplete)         em0 expired'

openbsd_arp_na_output_without_ip = \
    'Host                     Ethernet Address   Netif Expire     Flags\n'\
    '85.14.151.86             00:00:5e:00:01:05  carp5 permanent  l\n'\
    '91.226.28.0              (incomplete)         em0 expired'


class Test_checklayer2link(unittest.TestCase):
    """."""

    def test_check_probe_ok_with_ip_freebsd_output(self):
        check = checklayer2link.CheckLayer2Link('10.61.0.254')
        output = freebsd_arp_na_output_with_ip

        with mock.patch("checklayer2link.checklayer2link._popen") as _popen:
            _popen.return_value = output, ''
            probe = check.probe()
            self.assertEquals(probe.value, 1)

    def test_check_probe_ko_without_ip_freebsd_output(self):
        check = checklayer2link.CheckLayer2Link('10.61.0.254')
        output = freebsd_arp_na_output_without_ip

        with mock.patch("checklayer2link.checklayer2link._popen") as _popen:
            _popen.return_value = output, ''
            probe = check.probe()
            self.assertEquals(probe.value, 0)

    def test_check_probe_ok_with_ip_openbsd_output(self):
        output = openbsd_arp_na_output_with_ip
        check = checklayer2link.CheckLayer2Link('10.61.0.254')

        with mock.patch("checklayer2link.checklayer2link._popen") as _pop:
            _pop.return_value = output, ''
            probe = check.probe('OpenBSD')
            self.assertEquals(probe.value, 1)

    def test_check_probe_ko_without_ip_openbsd_output(self):
        output = openbsd_arp_na_output_without_ip
        check = checklayer2link.CheckLayer2Link('10.61.0.254')

        with mock.patch("checklayer2link.checklayer2link._popen") as _pop:
            _pop.return_value = output, ''
            probe = check.probe('OpenBSD')
            self.assertEquals(probe.value, 0)

    def test__find_ip_arp_table_error(self):
        check = checklayer2link.CheckLayer2Link('10.61.0.254')
        err_output = "An error occured!\n'"
        with mock.patch("checklayer2link.checklayer2link._popen") as _pop:
            _pop.return_value = '', err_output
            with self.assertRaises(CheckError):
                check.probe()  # NOQA


class Test_AuditSummary(unittest.TestCase):

    def test_ok(self):
        from nagiosplugin.result import Result, Results
        from nagiosplugin.state import Ok
        from checklayer2link.checklayer2link import AuditSummary
        from checklayer2link.checklayer2link import CheckLayer2Link
        resource = CheckLayer2Link('192.168.0.1')
        results = Results()
        ok_r1 = Result(Ok, '', nagiosplugin.Metric('mac', 1, context='arp',
                       resource=resource))
        results.add(ok_r1)
        summary = AuditSummary()
        sum_ok = summary.ok(results)
        self.assertEquals(sum_ok, 'layer 2 for ip 192.168.0.1 is up')

    def test_critical(self):
        from nagiosplugin.result import Result, Results
        from nagiosplugin.state import Critical
        from checklayer2link.checklayer2link import AuditSummary
        from checklayer2link.checklayer2link import CheckLayer2Link
        resource = CheckLayer2Link('192.168.0.1')
        results = Results()
        crit_r1 = Result(Critical, '', nagiosplugin.Metric('mac', 0,
                         context='arp', resource=resource))
        results.add(crit_r1)
        summary = AuditSummary()
        sum_pb = summary.problem(results)
        self.assertEquals(sum_pb, 'layer 2 for ip 192.168.0.1 is down')
