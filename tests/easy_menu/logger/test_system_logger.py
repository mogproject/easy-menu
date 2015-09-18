# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import os
from tests.universal import TestCase
from easy_menu.logger.system_logger import SystemLogger


class TestSystemLogger(TestCase):
    def test_logger(self):
        # should run only in CI
        if os.environ.get('CI', '').lower() == 'true':
            logger = SystemLogger()

            logger.info('Info message.')
            logger.warn('Warn message.')
            logger.error('Error message.')

    def test_logger_unicode(self):
        # should run only in CI
        if os.environ.get('CI', '').lower() == 'true':
            logger = SystemLogger()

            logger.info('情報 メッセージ')
            logger.warn('警戒 メッセージ')
            logger.error('エラー メッセージ')
