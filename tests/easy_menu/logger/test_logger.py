from __future__ import division, print_function, absolute_import, unicode_literals

from mog_commons.unittest import TestCase
from tests.easy_menu.logger.mock_logger import MockLogger


class TestLogger(TestCase):
    def test_logger(self):
        ml = MockLogger()
        ml.info('Info message.')
        ml.warn('Warn message.')
        ml.error('Error message.')
        self.assertEqual(ml.buffer, [
            (6, '[INFO] Info message.'),
            (4, '[WARN] Warn message.'),
            (3, '[ERROR]Error message.'),
        ])
