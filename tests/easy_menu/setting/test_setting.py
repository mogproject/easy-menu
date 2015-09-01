# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import os
from easy_menu.setting.setting import Setting, ConfigError, SettingError
from tests.universal import TestCase
from tests.fake_io import captured_output


class TestSetting(TestCase):
    def _assert_system_exit(self, expected_code, f):
        with self.assertRaises(SystemExit) as cm:
            f()
        if isinstance(cm.exception, int):
            self.assertEqual(cm.exception, expected_code)
        else:
            self.assertEqual(cm.exception.code, expected_code)

    def _with_output(self, func, expect, expect_stdout, expect_stderr):
        with captured_output() as (out, err):
            self.assertEqual(func(), expect)
        self.assertEqual(out.getvalue(), expect_stdout)
        self.assertEqual(err.getvalue(), expect_stderr)

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

    def test_find_lang(self):
        s = Setting()
        old = os.environ['LANG']

        del os.environ['LANG']
        self.assertEqual(s._find_lang('ja_JP'), 'ja_JP')
        s._find_lang(None).islower()  # return value depends on the system

        os.environ['LANG'] = 'en_US'
        self.assertEqual(s._find_lang(None), 'en_US')

        os.environ['LANG'] = old

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
        with captured_output() as (out, err):
            self._assert_system_exit(2, lambda: Setting().parse_args(['easy-menu', 'a', 'b']))
        self.assertEqual(out.getvalue(), '\n'.join([
            'Usage: setup.py [options...] [<config_path> | <config_url>]',
            '',
            'Options:',
            "  --version             show program's version number and exit",
            '  -h, --help            show this help message and exit',
            '  --encode=ENCODING     set output encoding to ENCODING',
            '  --lang=LANG           set language to LANG (in RFC 1766 format)',
            '  -d DIR, --work-dir=DIR',
            '                        set working directory to DIR',
            ''
        ]))
        self.assertEqual(err.getvalue(), '')

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
        self._with_output(
            lambda: Setting()._load_data(False, 'tests/resources/minimum.yml'),
            {'': []}, 'Reading file: tests/resources/minimum.yml\n', ''
        )

        self._with_output(
            lambda: Setting()._load_data(False, 'tests/resources/nested.yml'),
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
                {'Menu 6': 'echo 6'}]},
            'Reading file: tests/resources/nested.yml\n',
            ''
        )
        self._with_output(
            lambda: Setting()._load_data(False, 'tests/resources/with_meta.yml'),
            {'meta': {'work_dir': '/tmp'},
             'Main Menu': [{'Menu 1': 'echo 1'}, {'Menu 2': 'echo 2'}, {'Menu 3': 'echo 3'}, {'Menu 4': 'echo 4'},
                           {'Menu 5': 'echo 5'}, {'Menu 6': 'echo 6'}]},
            'Reading file: tests/resources/with_meta.yml\n',
            ''
        )
        self._with_output(
            lambda: Setting(cache={(False, 'https://example.com/foo.yml'): {
                'Main Menu': [{'Menu 1': 'echo 1'}, {'Menu 2': 'echo 2'}]}
            })._load_data(False, 'https://example.com/foo.yml'),
            {'Main Menu': [{'Menu 1': 'echo 1'}, {'Menu 2': 'echo 2'}]},
            '',
            ''
        )
        self._with_output(
            lambda: Setting()._load_data(True, """echo '{"Main Menu":[{"Menu 1":"echo 1"},{"Menu 2":"echo 2"}]}'"""),
            {'Main Menu': [{'Menu 1': 'echo 1'}, {'Menu 2': 'echo 2'}]},
            """Executing: echo '{"Main Menu":[{"Menu 1":"echo 1"},{"Menu 2":"echo 2"}]}'\n""",
            ''
        )
        self._with_output(
            lambda: Setting(work_dir=os.path.abspath('tests/resources'))._load_data(False, 'minimum.yml'),
            {'': []},
            'Reading file: %s\n' % self._testfile('minimum.yml'),
            ''
        )
        # SJIS
        self._with_output(
            lambda: Setting(encoding='sjis')._load_data(False, 'tests/resources/sjis_ja.yml'),
            {
                "メインメニュー": [
                    {"サービス稼動状態確認": "echo 'サービス稼動状態確認'"},
                    {"サーバリソース状況確認": "echo 'サーバリソース状況確認'"},
                    {"業務状態制御メニュー": [
                        {"業務状態確認": "echo '業務状態確認'"},
                        {"業務開始": "echo '業務開始'"},
                        {"業務終了": "echo '業務終了'"}
                    ]},
                    {"Webサービス制御メニュー": [
                        {"Webサービス状態確認": "echo 'Webサービス状態確認'"},
                        {"Webサービス起動": "echo 'Webサービス起動'"},
                        {"Webサービス停止": "echo 'Webサービス停止'"}
                    ]},
                    {"サーバ再起動": "echo 'サーバ再起動'"}
                ]
            },
            'Reading file: tests/resources/sjis_ja.yml\n',
            ''
        )

    def test_load_data_error(self):
        self.assertRaisesRegexp(
            SettingError,
            '^Not found configuration file[.]$',
            lambda: Setting()._load_data(False, None)
        )

        inputs = [
            ('error_not_exist.yml', 'Failed to open[.]'),
            ('error_parser.yml', 'YAML format error: expected \'<document start>\', but found \'<scalar>\'\n'
                                 '  in "<unicode string>", line 1, column 3:\n    \'\':1\n      \^'),
            ('error_scanner.yml',
             'YAML format error: while scanning a quoted scalar\n  in "<unicode string>", line 1, column 1:\n    "'
             '\n    \^\nfound unexpected end of stream\n  in "<unicode string>", line 2, column 1:\n    \n    \^')
        ]

        for filename, expect in inputs:
            with captured_output() as (out, err):
                self.assertRaisesRegexp(
                    ConfigError,
                    '^Configuration error: %s: %s$' % (self._testfile(filename), expect),
                    lambda: Setting(config_path=self._testfile(filename)).load_config()
                )
                self.assertEqual(out.getvalue(), 'Reading file: %s\n' % self._testfile(filename))
                self.assertEqual(err.getvalue(), '')

    def test_load_meta(self):
        self._with_output(
            lambda: Setting(self._testfile('minimum.yml')).load_meta().work_dir,
            os.path.join(os.path.abspath(os.path.curdir), 'tests/resources'),
            'Reading file: %s\n' % self._testfile('minimum.yml'),
            ''
        )
        self._with_output(
            lambda: Setting('https://example.com/foo.yml', cache={(False, 'https://example.com/foo.yml'): {
                'Main Menu': [{'Menu 1': 'echo 1'}, {'Menu 2': 'echo 2'}]}
            }).load_meta().work_dir,
            None,
            '',
            ''
        )
        self._with_output(
            lambda: Setting('https://example.com/foo.yml', cache={(False, 'https://example.com/foo.yml'): {
                'Main Menu': [{'Menu 1': 'echo 1'}, {'Menu 2': 'echo 2'}],
                'meta': {'work_dir': '/tmp'}}
            }).load_meta().work_dir,
            '/tmp',
            '',
            ''
        )
        self._with_output(
            lambda: Setting(self._testfile('with_meta.yml')).load_meta().work_dir,
            '/tmp',
            'Reading file: %s\n' % self._testfile('with_meta.yml'),
            ''
        )
        self._with_output(
            lambda: Setting(self._testfile('with_meta.yml'), work_dir='/var/tmp').load_meta().work_dir,
            '/tmp',
            'Reading file: %s\n' % self._testfile('with_meta.yml'),
            ''
        )

    def test_load_config(self):
        self._with_output(
            lambda: Setting(config_path=self._testfile('minimum.yml')).load_config().root_menu,
            {'': []},
            'Reading file: %s\n' % self._testfile('minimum.yml'),
            ''
        )
        self._with_output(
            lambda: Setting(config_path=self._testfile('flat.yml')).load_config().root_menu,
            {
                'Main Menu': [{'Menu 1': 'echo 1'}, {'Menu 2': 'echo 2'}, {'Menu 3': 'echo 3'}, {'Menu 4': 'echo 4'},
                              {'Menu 5': 'echo 5'}, {'Menu 6': 'echo 6'}]},
            'Reading file: %s/tests/resources/flat.yml\n' % os.path.abspath(os.path.curdir),
            ''
        )
        self._with_output(
            lambda: Setting(config_path=self._testfile('with_dynamic.yml')).load_config().root_menu,
            {'Main Menu': [{'Menu 1': 'echo 1'}, {'Sub Menu': [{'Menu 2': 'echo 2'}, {'Menu 3': 'echo 3'}]}]},
            'Reading file: %s/tests/resources/with_dynamic.yml\n' % os.path.abspath(os.path.curdir) +
            """Executing: echo '{"Sub Menu": [{"Menu 2": "echo 2"}, {"Menu 3": "echo 3"}]}'\n""",
            ''
        )

    def test_load_config_error(self):
        inputs = [
            ('error_command_only.yml', 'Root content must be list, not str[.]'),
            ('error_include_as_submenu.yml', '"include" section must have string content, not list[.]'),
            ('error_dynamic_as_submenu.yml', '"eval" section must have string content, not list[.]'),
            ('error_include_loop.yml', 'Nesting level too deep[.]'),
            ('error_key_only1.yml', 'Content must be string or list, not NoneType[.]'),
            ('error_key_only2.yml', 'Content must be string or list, not NoneType[.]'),
            ('error_meta_only.yml', 'Menu should have only one item, not 0[.]'),
            ('error_multiple_items.yml', 'Menu should have only one item, not 2[.]'),
            ('error_not_dict1.yml', 'Menu must be dict, not list[.]'),
            ('error_not_dict2.yml', 'Menu must be dict, not int[.]'),
        ]

        for filename, expect in inputs:
            with captured_output() as (out, err):
                self.assertRaisesRegexp(
                    ConfigError,
                    '^Configuration error: %s: %s$' % (self._testfile(filename), expect),
                    lambda: Setting(config_path=self._testfile(filename)).load_config()
                )
                self.assertEqual(out.getvalue(), 'Reading file: %s\n' % self._testfile(filename))
                self.assertEqual(err.getvalue(), '')
