import sys
import os
from easy_menu.setting.setting import Setting, ConfigError, SettingError

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class TestSetting(unittest.TestCase):
    def _assert_system_exit(self, expected_code, f):
        with self.assertRaises(SystemExit) as cm:
            f()
        if isinstance(cm.exception, int):
            self.assertEqual(cm.exception, expected_code)
        else:
            self.assertEqual(cm.exception.code, expected_code)

    def _testfile(self, filename):
        return os.path.join(os.path.abspath(os.path.curdir), 'tests/resources', filename)

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
        self._assert_system_exit(2, lambda: Setting().parse_args(['easy-menu', 'a', 'b']))

    def test_lookup_config(self):
        self.assertEqual(Setting('foo.yml').lookup_config(), Setting('foo.yml'))
        self.assertEqual(Setting().lookup_config(), Setting(os.path.abspath('easy-menu.yml')))
        self.assertEqual(
            Setting(work_dir='tests/resources').lookup_config(),
            Setting(os.path.abspath('easy-menu.yml'), work_dir='tests/resources'))

    def test_lookup_config_not_found(self):
        assert not os.path.exists('/easy-menu.yml'), 'This test assumes that there does not exist "/easy-menu.yml".'
        self.assertEqual(Setting(work_dir='/').lookup_config(), Setting(work_dir='/'))

    def test_load_data(self):
        self.assertEqual(
            Setting()._load_data(False, 'tests/resources/minimum.yml'),
            {'': []}
        )
        self.assertEqual(
            Setting()._load_data(False, 'tests/resources/nested.yml'),
            {'Main Menu': [
                {'Sub Menu 1': [
                    {'Menu 1': 'echo 1'},
                    {'Menu 2': 'echo 2'}
                ]},
                {'Sub Menu 2': [
                    {'Sub Menu 3': [
                        {'Menu 3': 'echo 3'},
                        {'Menu 4': 'echo 4'}
                    ]}, {'Menu 5': 'echo 5'}
                ]},
                {'Menu 6': 'echo 6'}]}
        )
        self.assertEqual(
            Setting()._load_data(False, 'tests/resources/with_meta.yml'),
            {'meta': {'work_dir': '/tmp'},
             'Main Menu': [{'Menu 1': 'echo 1'}, {'Menu 2': 'echo 2'}, {'Menu 3': 'echo 3'}, {'Menu 4': 'echo 4'},
                           {'Menu 5': 'echo 5'}, {'Menu 6': 'echo 6'}, ]}
        )
        self.assertEqual(
            Setting(cache={(False, 'https://example.com/foo.yml'): {
                'Main Menu': [{'Menu 1': 'echo 1'}, {'Menu 2': 'echo 2'}]}
            })._load_data(False, 'https://example.com/foo.yml'),
            {'Main Menu': [{'Menu 1': 'echo 1'}, {'Menu 2': 'echo 2'}]}
        )
        self.assertEqual(
            Setting()._load_data(True, """echo '{"Main Menu":[{"Menu 1":"echo 1"},{"Menu 2":"echo 2"}]}'"""),
            {'Main Menu': [{'Menu 1': 'echo 1'}, {'Menu 2': 'echo 2'}]}
        )
        self.assertEqual(
            Setting(work_dir=os.path.abspath('tests/resources'))._load_data(False, 'minimum.yml'),
            {'': []}
        )

    def test_load_data_error(self):
        def f(filename, err, msg):
            with self.assertRaises(err) as cm:
                Setting()._load_data(False, os.path.join('tests/resources', filename))
            self.assertEqual(cm.exception.args[0], msg)

        with self.assertRaises(SettingError) as cm:
            Setting()._load_data(False, None)
        self.assertEqual(cm.exception.args[0], 'Not found configuration file.')

        f('error_not_exist.yml', ConfigError, 'Failed to open: tests/resources/error_not_exist.yml')
        f('error_parser.yml', ConfigError,
          'YAML format error: tests/resources/error_parser.yml: expected \'<document start>\', but found \'<scalar>\'\n'
          '  in "tests/resources/error_parser.yml", line 1, column 3')
        f('error_scanner.yml', ConfigError,
          'YAML format error: tests/resources/error_scanner.yml: while scanning a quoted scalar\n  in "tests/resources/'
          'error_scanner.yml", line 1, column 1\nfound unexpected end of stream\n  in "tests/resources/error_scanner.ym'
          'l", line 2, column 1')

    def test_load_meta(self):
        self.assertEqual(
            Setting(self._testfile('minimum.yml')).load_meta().work_dir,
            os.path.join(os.path.abspath(os.path.curdir), 'tests/resources')
        )
        self.assertEqual(
            Setting('https://example.com/foo.yml', cache={(False, 'https://example.com/foo.yml'): {
                'Main Menu': [{'Menu 1': 'echo 1'}, {'Menu 2': 'echo 2'}]}
            }).load_meta().work_dir,
            None
        )
        self.assertEqual(
            Setting('https://example.com/foo.yml', cache={(False, 'https://example.com/foo.yml'): {
                'Main Menu': [{'Menu 1': 'echo 1'}, {'Menu 2': 'echo 2'}],
                'meta': {'work_dir': '/tmp'}}
            }).load_meta().work_dir,
            '/tmp'
        )
        self.assertEqual(Setting(self._testfile('with_meta.yml')).load_meta().work_dir, '/tmp')
        self.assertEqual(Setting(self._testfile('with_meta.yml'), work_dir='/var/tmp').load_meta().work_dir, '/tmp')
