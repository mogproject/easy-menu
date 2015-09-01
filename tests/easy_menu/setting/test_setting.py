# -*- coding: utf-8 -*-

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

        s3 = Setting('https://example.com/resources/minimum.yml')
        self.assertEqual(s3.config_path, 'https://example.com/resources/minimum.yml')
        self.assertEqual(s3.work_dir, None)
        self.assertEqual(s3.root_menu, {})

        s4 = Setting('tests/resources/minimum.yml', work_dir='/tmp')
        self.assertEqual(s4.config_path, 'tests/resources/minimum.yml')
        self.assertEqual(s4.work_dir, '/tmp')
        self.assertEqual(s4.root_menu, {})

        s5 = Setting('https://example.com/resources/minimum.yml', work_dir='/tmp')
        self.assertEqual(s5.config_path, 'https://example.com/resources/minimum.yml')
        self.assertEqual(s5.work_dir, '/tmp')
        self.assertEqual(s5.root_menu, {})

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

        import easy_menu.setting.setting

        old = easy_menu.setting.setting.DEFAULT_CONFIG_NAME
        easy_menu.setting.setting.DEFAULT_CONFIG_NAME = 'easy-menu.example.yml'

        try:
            self.assertEqual(Setting().lookup_config(), Setting(os.path.abspath('easy-menu.example.yml')))
            self.assertEqual(
                Setting(work_dir='tests/resources').lookup_config(),
                Setting(os.path.abspath('easy-menu.example.yml'), work_dir='tests/resources'))
        finally:
            easy_menu.setting.setting.DEFAULT_CONFIG_NAME = old

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
                           {'Menu 5': 'echo 5'}, {'Menu 6': 'echo 6'}]}
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
        # SJIS
        self.assertEqual(
            Setting(encoding='sjis')._load_data(False, 'tests/resources/sjis_ja.yml'),
            {
                u"メインメニュー": [
                    {u"サービス稼動状態確認": u"echo 'サービス稼動状態確認'"},
                    {u"サーバリソース状況確認": u"echo 'サーバリソース状況確認'"},
                    {u"業務状態制御メニュー": [
                        {u"業務状態確認": u"echo '業務状態確認'"},
                        {u"業務開始": u"echo '業務開始'"},
                        {u"業務終了": u"echo '業務終了'"}
                    ]},
                    {u"Webサービス制御メニュー": [
                        {u"Webサービス状態確認": u"echo 'Webサービス状態確認'"},
                        {u"Webサービス起動": u"echo 'Webサービス起動'"},
                        {u"Webサービス停止": u"echo 'Webサービス停止'"}
                    ]},
                    {u"サーバ再起動": u"echo 'サーバ再起動'"}
                ]
            }
        )

    def test_load_data_error(self):
        def f(filename, err, msg):
            with self.assertRaises(err) as cm:
                Setting()._load_data(False, os.path.join('tests/resources', filename))
            self.assertEqual(cm.exception.args[0], msg)

        with self.assertRaises(SettingError) as cm:
            Setting()._load_data(False, None)
        self.assertEqual(cm.exception.args[0], 'Not found configuration file.')

        f('error_not_exist.yml', ConfigError,
          'Configuration error: tests/resources/error_not_exist.yml: Failed to open.')
        f('error_parser.yml', ConfigError,
          'Configuration error: tests/resources/error_parser.yml: '
          'YAML format error: expected \'<document start>\', but found \'<scalar>\'\n'
          '  in "<unicode string>", line 1, column 3:\n    \'\':1\n      ^')
        f('error_scanner.yml', ConfigError,
          'Configuration error: tests/resources/error_scanner.yml: '
          'YAML format error: while scanning a quoted scalar\n  in "<unicode string>", line 1, column 1:\n    "\n    ^'
          '\nfound unexpected end of stream\n  in "<unicode string>", line 2, column 1:\n    \n    ^')

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

    def test_load_config(self):
        s = Setting(config_path=self._testfile('minimum.yml')).load_config()
        self.assertEqual(s.root_menu, {'': []})

        s = Setting(config_path=self._testfile('flat.yml')).load_config()
        self.assertEqual(s.root_menu, {
            'Main Menu': [{'Menu 1': 'echo 1'}, {'Menu 2': 'echo 2'}, {'Menu 3': 'echo 3'}, {'Menu 4': 'echo 4'},
                          {'Menu 5': 'echo 5'}, {'Menu 6': 'echo 6'}]})

        s = Setting(config_path=self._testfile('with_dynamic.yml')).load_config()
        self.assertEqual(s.root_menu, {
            'Main Menu': [{'Menu 1': 'echo 1'},
                          {'Sub Menu': [{'Menu 2': 'echo 2'}, {'Menu 3': 'echo 3'}]}]})

    def test_load_config_error(self):
        def prefixed(filename):
            return 'Configuration error: %s: ' % self._testfile(filename)

        def f(filename, msg):
            with self.assertRaises(ConfigError) as cm:
                Setting(config_path=self._testfile(filename)).load_config()
            self.assertEqual(cm.exception.args[0], prefixed(filename) + msg)

        f('error_command_only.yml', 'Root content must be list, not str.')
        f('error_include_as_submenu.yml', '"include" section must have string content, not list.')
        f('error_dynamic_as_submenu.yml', '"eval" section must have string content, not list.')
        f('error_include_loop.yml', 'Nesting level too deep.')
        f('error_key_only1.yml', 'Content must be string or list, not NoneType.')
        f('error_key_only2.yml', 'Content must be string or list, not NoneType.')
        f('error_meta_only.yml', 'Menu should have only one item, not 0.')
        f('error_multiple_items.yml', 'Menu should have only one item, not 2.')
        f('error_not_dict1.yml', 'Menu must be dict, not list.')
        f('error_not_dict2.yml', 'Menu must be dict, not int.')
