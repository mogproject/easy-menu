# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import sys
import os
from contextlib import contextmanager
from easy_menu import easy_menu
from easy_menu.util import network_util, string_util
from tests.universal import TestCase, mock
from tests.easy_menu.logger.mock_logger import MockLogger
from tests.fake_io import FakeInput, captured_output
from tests.util.assert_util import assert_output


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

    @mock.patch('easy_menu.easy_menu.SystemLogger')
    def test_main(self, mock_logger):
        self.maxDiff = None

        ml = MockLogger()
        mock_logger.return_value = ml
        _in = FakeInput(''.join(['1yx', '2yx', '31yx0', '41yx0', '.0']))

        with self.with_argv(['easy-menu', 'tests/resources/integration_1.yml', '--lang', 'us']):
            host = network_util.get_hostname()
            user = network_util.get_username()

            with assert_output(self, 'tests/resources/expect/integration_test.txt.j2', {
                'base_dir': os.path.abspath(os.path.curdir),
                'header': string_util.edge_just('Host: ' + host, 'User: ' + user, 78),
                'null': '',
            }) as out:
                self.assertEqual(easy_menu.main(_in, out), 0)

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
            with captured_output() as (out, err):
                self.assertEqual(easy_menu.main(), 2)
                self.assertEqual(out.getvalue(), '\n'.join([
                    'Reading file: %s' % path,
                    'ConfigError: %s: Failed to open.' % path,
                    ''
                ]))
                self.assertEqual(err.getvalue(), '')
        self.assertEqual(ml.buffer, [])
