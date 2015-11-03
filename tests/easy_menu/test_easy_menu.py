# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import sys
import os
import socket
import getpass
from contextlib import contextmanager
from easy_menu import easy_menu
from mog_commons.string import *
from mog_commons.unittest import TestCase, base_unittest, FakeInput
from tests.easy_menu.logger.mock_logger import MockLogger

if sys.version_info < (3, 3):
    import mock
else:
    from unittest import mock


class TestTerminal(TestCase):
    @staticmethod
    @contextmanager
    def with_argv(argv):
        old = sys.argv
        try:
            sys.argv = argv
            yield
        finally:
            sys.argv = old

    @base_unittest.skipUnless(os.name != 'nt', 'requires POSIX compatible')
    @mock.patch('easy_menu.easy_menu.SystemLogger')
    def test_main(self, mock_logger):
        self.maxDiff = None

        ml = MockLogger()
        mock_logger.return_value = ml
        _in = FakeInput(''.join(['1yx', '2yx', '31yx0', '41yx00', '.0']))

        with self.with_argv(['easy-menu', 'tests/resources/integration_1.yml', '--lang', 'us']):
            host = socket.gethostname()
            user = getpass.getuser()

            with self.withAssertOutputFile('tests/resources/expect/integration_test.txt.j2', {
                'base_dir': os.path.abspath(os.path.curdir),
                'header': edge_just('Host: ' + host, 'User: ' + user, 78)
            }) as out:
                self.assertEqual(easy_menu.main(_in, out, out, False), 0)

            self.assertEqual(ml.buffer, [
                (6, '[INFO] Command started: exit 1'),
                (6, '[INFO] Command ended with return code: 1'),
                (6, '[INFO] Command started: exit 2'),
                (6, '[INFO] Command ended with return code: 2'),
                (6, '[INFO] Command started: exit 3'),
                (6, '[INFO] Command ended with return code: 3'),
                (6, '[INFO] Command started: exit 4'),
                (6, '[INFO] Command ended with return code: 4'),
            ])

    @mock.patch('easy_menu.easy_menu.SystemLogger')
    def test_main_not_found(self, mock_logger):
        ml = MockLogger()
        mock_logger.return_value = ml

        path = os.path.abspath('tests/resources/error/error_not_exist.yml')
        with self.with_argv(['easy-menu', path]):
            expect_stdout = '\n'.join([
                'Reading file: %s' % path,
                'ConfigError: %s: Failed to open.' % path,
                ''
            ])
            with self.withAssertOutput(expect_stdout, '') as (stdout, stderr):
                self.assertEqual(easy_menu.main(stdout=stdout, stderr=stderr), 2)

        self.assertEqual(ml.buffer, [])
