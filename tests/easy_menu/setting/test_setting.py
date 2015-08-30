import sys
import os
from easy_menu.setting.setting import Setting

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class TestSetting(unittest.TestCase):
    def test_init(self):
        s1 = Setting()
        self.assertEqual(s1.config_path, None)
        self.assertEqual(s1.work_dir, None)
        self.assertEqual(s1.root_menu, {})
        self.assertEqual(s1.encoding, None)

        s2 = Setting('tests/resources/minimum.yml')
        self.assertEqual(s2.config_path, 'tests/resources/minimum.yml')
        self.assertEqual(s2.work_dir, 'tests/resources')
        self.assertEqual(s2.root_menu, {})
        self.assertEqual(s2.encoding, None)

        s3 = Setting('https://example.com/resources/minimum.yml')
        self.assertEqual(s3.config_path, 'https://example.com/resources/minimum.yml')
        self.assertEqual(s3.work_dir, None)
        self.assertEqual(s3.root_menu, {})
        self.assertEqual(s3.encoding, None)

        s4 = Setting('tests/resources/minimum.yml', work_dir='/tmp')
        self.assertEqual(s4.config_path, 'tests/resources/minimum.yml')
        self.assertEqual(s4.work_dir, '/tmp')
        self.assertEqual(s4.root_menu, {})
        self.assertEqual(s4.encoding, None)

        s5 = Setting('https://example.com/resources/minimum.yml', work_dir='/tmp')
        self.assertEqual(s5.config_path, 'https://example.com/resources/minimum.yml')
        self.assertEqual(s5.work_dir, '/tmp')
        self.assertEqual(s5.root_menu, {})
        self.assertEqual(s5.encoding, None)

    def test_is_url(self):
        self.assertEqual(Setting()._is_url('http://example.com/foo.yml'), True)
        self.assertEqual(Setting()._is_url('https://example.com/foo.yml'), True)
        self.assertEqual(Setting()._is_url('ftp://example.com/foo.yml'), False)
        self.assertEqual(Setting()._is_url('/etc/foo/bar.yml'), False)

    def test_parse_args(self):
        def abspath(path):
            return os.path.join(os.path.abspath(os.path.curdir), path)

        self.assertEqual(
            Setting().parse_args(['easy-menu']),
            Setting()
        )
        self.assertEqual(
            Setting().parse_args(['easy-menu', 'xyz.yml']),
            Setting(config_path=abspath('xyz.yml'))
        )
        self.assertEqual(
            Setting().parse_args(['easy-menu', 'http://example.com/xyz.yml']),
            Setting(config_path='http://example.com/xyz.yml')
        )
        self.assertEqual(
            Setting().parse_args(['easy-menu', 'http://example.com/xyz.yml', '-d', '/tmp']),
            Setting(config_path='http://example.com/xyz.yml', work_dir='/tmp')
        )
        self.assertEqual(
            Setting().parse_args(['easy-menu', 'http://example.com/xyz.yml', '--work-dir', '/tmp']),
            Setting(config_path='http://example.com/xyz.yml', work_dir='/tmp')
        )
        self.assertEqual(
            Setting().parse_args(['easy-menu', '/path/to/minimum.yml', '--encode', 'utf-8']),
            Setting(config_path='/path/to/minimum.yml', work_dir='/path/to', encoding='utf-8')
        )

    def test_parse_args_error(self):
        self.assertRaises(SystemExit, Setting().parse_args, ['easy-menu', 'a', 'b'])
