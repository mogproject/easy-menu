import sys
from easy_menu.setting.setting import Setting

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class TestSetting(unittest.TestCase):
    def test_setting_init(self):
        s1 = Setting()
        self.assertEqual(s1.config_path, None)
        self.assertEqual(s1.is_url, False)
        self.assertEqual(s1.work_dir, None)
        self.assertEqual(s1.root_menu, {})
        self.assertEqual(s1.encoding, None)

        s2 = Setting('tests/resources/minimum.yml')
        self.assertEqual(s2.config_path, 'tests/resources/minimum.yml')
        self.assertEqual(s2.is_url, False)
        self.assertEqual(s2.work_dir, 'tests/resources')
        self.assertEqual(s2.root_menu, {})
        self.assertEqual(s2.encoding, None)

        s3 = Setting('https://example.com/resources/minimum.yml')
        self.assertEqual(s3.config_path, 'https://example.com/resources/minimum.yml')
        self.assertEqual(s3.is_url, True)
        self.assertEqual(s3.work_dir, None)
        self.assertEqual(s3.root_menu, {})
        self.assertEqual(s3.encoding, None)

        s4 = Setting('tests/resources/minimum.yml', work_dir='/tmp')
        self.assertEqual(s4.config_path, 'tests/resources/minimum.yml')
        self.assertEqual(s4.is_url, False)
        self.assertEqual(s4.work_dir, '/tmp')
        self.assertEqual(s4.root_menu, {})
        self.assertEqual(s4.encoding, None)

        s5 = Setting('https://example.com/resources/minimum.yml', work_dir='/tmp')
        self.assertEqual(s5.config_path, 'https://example.com/resources/minimum.yml')
        self.assertEqual(s5.is_url, True)
        self.assertEqual(s5.work_dir, '/tmp')
        self.assertEqual(s5.root_menu, {})
        self.assertEqual(s5.encoding, None)
