# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import os
from tests.universal import TestCase, unittest
from easy_menu.logger.system_logger import SystemLogger


class TestSystemLogger(TestCase):
    @unittest.skipUnless(os.environ.get('CI', '').lower() == 'true', 'run only in CI')
    def test_logger(self):
        logger = SystemLogger()
        logger.info('Info message.')
        logger.warn('Warn message.')
        logger.error('Error message.')

    @unittest.skipUnless(os.environ.get('CI', '').lower() == 'true', 'run only in CI')
    def test_logger_unicode(self):
        logger = SystemLogger()
        logger.info('情報 メッセージ')
        logger.warn('警戒 メッセージ')
        logger.error('エラー メッセージ')
