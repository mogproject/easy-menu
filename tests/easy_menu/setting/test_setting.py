# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import os
import six

from easy_menu.setting.setting import Setting
from easy_menu.exceptions import ConfigError, SettingError, EncodingError
from tests.universal import TestCase, mock


class TestSetting(TestCase):
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

    def test_find_encoding(self):
        import io
        import codecs

        if six.PY2:
            out = codecs.getwriter('sjis')
            out.encoding = 'sjis'
        else:
            out = io.TextIOWrapper(six.StringIO(), 'sjis')

        self.assertEqual(Setting()._find_encoding(None, out), 'sjis')
        self.assertEqual(Setting(stdout=out).encoding, 'sjis')
        self.assertEqual(Setting(encoding='utf-8', stdout=out).encoding, 'utf-8')

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
        expect_stdout = '\n'.join([
            'Usage: setup.py [options...] [<config_path> | <config_url>]',
            '',
            'Options:',
            "  --version             show program's version number and exit",
            '  -h, --help            show this help message and exit',
            '  --encode=ENCODING     set output encoding to ENCODING',
            '  --lang=LANG           set language to LANG (in RFC 1766 format)',
            '  --width=WIDTH         set window width to WIDTH',
            '  -d DIR, --work-dir=DIR',
            '                        set working directory to DIR',
            ''
        ])

        with self.withAssertOutputInject(expect_stdout, '') as (out, err):
            self._assert_system_exit(2, lambda: Setting(stdout=out, stderr=err).parse_args(['easy-menu', 'a', 'b']))

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
        with self.withAssertOutput('Reading file: tests/resources/minimum.yml\n', '') as (out, err):
            self.assertEqual(
                Setting(stdout=out, stderr=err)._load_data(False, 'tests/resources/minimum.yml'),
                {'': []}
            )

        with self.withAssertOutput('Reading file: tests/resources/nested.yml\n', '') as (out, err):
            self.assertEqual(Setting(stdout=out, stderr=err)._load_data(False, 'tests/resources/nested.yml'),
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
        with self.withAssertOutput('Reading file: tests/resources/with_meta.yml\n', '') as (out, err):
            self.assertEqual(
                Setting(stdout=out, stderr=err)._load_data(False, 'tests/resources/with_meta.yml'),
                {'meta': {'work_dir': '/tmp'},
                 'Main Menu': [{'Menu 1': 'echo 1'}, {'Menu 2': 'echo 2'}, {'Menu 3': 'echo 3'}, {'Menu 4': 'echo 4'},
                               {'Menu 5': 'echo 5'}, {'Menu 6': 'echo 6'}]}
            )
        with self.withAssertOutput('', '') as (out, err):
            self.assertEqual(
                Setting(cache={(False, 'https://example.com/foo.yml'): {
                    'Main Menu': [{'Menu 1': 'echo 1'}, {'Menu 2': 'echo 2'}]}
                }, stdout=out, stderr=err)._load_data(False, 'https://example.com/foo.yml'),
                {'Main Menu': [{'Menu 1': 'echo 1'}, {'Menu 2': 'echo 2'}]}
            )
        with self.withAssertOutput(
                """Executing: echo '{"Main Menu":[{"Menu 1":"echo 1"},{"Menu 2":"echo 2"}]}'\n""", '') as (out, err):
            self.assertEqual(Setting(stdout=out, stderr=err)._load_data(
                True,
                """echo '{"Main Menu":[{"Menu 1":"echo 1"},{"Menu 2":"echo 2"}]}'"""),
                {'Main Menu': [{'Menu 1': 'echo 1'}, {'Menu 2': 'echo 2'}]}
            )
        with self.withAssertOutput('Reading file: %s\n' % self._testfile('minimum.yml'), '') as (out, err):
            self.assertEqual(
                Setting(work_dir=os.path.abspath('tests/resources'), stdout=out, stderr=err)._load_data(False,
                                                                                                        'minimum.yml'),
                {'': []}
            )
        # SJIS
        with self.withAssertOutput('Reading file: tests/resources/sjis_ja.yml\n', '') as (out, err):
            self.assertEqual(
                Setting(encoding='sjis', stdout=out, stderr=err)._load_data(False, 'tests/resources/sjis_ja.yml'),
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
                }
            )

    @mock.patch('easy_menu.setting.setting.urlopen')
    def test_load_data_http(self, urlopen_mock):
        # create a mock
        urlopen_mock.return_value.read.return_value = b'{"title":[{"a":"x"},{"b":"y"}]}'

        with self.withAssertOutput('Reading from URL: http://localhost/xxx.yml\n', '') as (out, err):
            self.assertEqual(
                Setting(stdout=out, stderr=err)._load_data(False, 'http://localhost/xxx.yml'),
                {'title': [{'a': 'x'}, {'b': 'y'}]}
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
            path = self._testfile(os.path.join('error', filename))
            with self.withAssertOutput('Reading file: %s\n' % path, '') as (out, err):
                self.assertRaisesRegexp(
                    ConfigError,
                    '^%s: %s$' % (path, expect),
                    lambda: Setting(config_path=path, stdout=out, stderr=err).load_config()
                )

    def test_load_data_encoding_error_file(self):
        path = self._testfile('sjis_ja.yml')
        with self.withAssertOutput('Reading file: %s\n' % path, '') as (out, err):
            self.assertRaisesRegexp(
                EncodingError,
                '^Failed to decode with utf-8: %s$' % path.replace('.', '\.'),
                lambda: Setting(encoding='utf-8', stdout=out, stderr=err)._load_data(False, path)
            )

    @mock.patch('easy_menu.setting.setting.urlopen')
    def test_load_data_encoding_error_http(self, urlopen_mock):
        # create a mock
        urlopen_mock.return_value.read.return_value = '{"あ":[{"い":"う"},{"え":"お"}]}'.encode('sjis')

        path = 'http://localhost/xxx.yml'
        with self.withAssertOutput('Reading from URL: %s\n' % path, '') as (out, err):
            self.assertRaisesRegexp(
                EncodingError,
                '^Failed to decode with utf-8: %s$' % path.replace('.', '\.'),
                lambda: Setting(encoding='utf-8', stdout=out, stderr=err)._load_data(False, path)
            )

    def test_load_data_encoding_error_cmd(self):
        cmd = 'cat tests/resources/sjis_ja.yml'  # output should be SJIS

        with self.withAssertOutput('Executing: %s\n' % cmd, '') as (out, err):
            self.assertRaisesRegexp(
                EncodingError,
                '^Failed to decode with utf-8: %s$' % cmd,
                lambda: Setting(encoding='utf-8', stdout=out, stderr=err)._load_data(True, cmd)
            )

    def test_load_meta(self):
        with self.withAssertOutput('Reading file: %s\n' % self._testfile('minimum.yml'), '') as (out, err):
            self.assertEqual(
                Setting(self._testfile('minimum.yml'), stdout=out, stderr=err).load_meta().work_dir,
                os.path.join(os.path.abspath(os.path.curdir), 'tests/resources')
            )
        with self.withAssertOutput('', '') as (out, err):
            self.assertEqual(
                Setting('https://example.com/foo.yml', cache={(False, 'https://example.com/foo.yml'): {
                    'Main Menu': [{'Menu 1': 'echo 1'}, {'Menu 2': 'echo 2'}]}
                }, stdout=out, stderr=err).load_meta().work_dir,
                None,
            )
        with self.withAssertOutput('', '') as (out, err):
            self.assertEqual(
                Setting('https://example.com/foo.yml', cache={(False, 'https://example.com/foo.yml'): {
                    'Main Menu': [{'Menu 1': 'echo 1'}, {'Menu 2': 'echo 2'}],
                    'meta': {'work_dir': '/tmp'}}
                }, stdout=out, stderr=err).load_meta().work_dir,
                '/tmp'
            )
        with self.withAssertOutput('Reading file: %s\n' % self._testfile('with_meta.yml'), '') as (out, err):
            self.assertEqual(
                Setting(self._testfile('with_meta.yml'), stdout=out, stderr=err).load_meta().work_dir,
                '/tmp'
            )
        with self.withAssertOutput('Reading file: %s\n' % self._testfile('with_meta.yml'), '') as (out, err):
            self.assertEqual(
                Setting(self._testfile('with_meta.yml'), work_dir='/var/tmp', stdout=out,
                        stderr=err).load_meta().work_dir,
                '/tmp'
            )

    def test_load_config(self):
        with self.withAssertOutput('Reading file: %s\n' % self._testfile('minimum.yml'), '') as (out, err):
            self.assertEqual(
                Setting(config_path=self._testfile('minimum.yml'), stdout=out, stderr=err).load_config().root_menu,
                {'': []}
            )
        with self.withAssertOutput('Reading file: %s/tests/resources/flat.yml\n' % os.path.abspath(os.path.curdir),
                                   '') as (out, err):
            self.assertEqual(
                Setting(config_path=self._testfile('flat.yml'), stdout=out, stderr=err).load_config().root_menu,
                {
                    'Main Menu': [{'Menu 1': 'echo 1'}, {'Menu 2': 'echo 2'}, {'Menu 3': 'echo 3'},
                                  {'Menu 4': 'echo 4'},
                                  {'Menu 5': 'echo 5'}, {'Menu 6': 'echo 6'}]}
            )

        expect = '\n'.join([
            'Reading file: %s/tests/resources/with_dynamic.yml' % os.path.abspath(os.path.curdir),
            """Executing: echo '{"Sub Menu": [{"Menu 2": "echo 2"}, {"Menu 3": "echo 3"}]}'\n"""
        ])
        with self.withAssertOutput(expect, '') as (out, err):
            self.assertEqual(
                Setting(config_path=self._testfile('with_dynamic.yml'), stdout=out, stderr=err).load_config().root_menu,
                {'Main Menu': [{'Menu 1': 'echo 1'}, {'Sub Menu': [{'Menu 2': 'echo 2'}, {'Menu 3': 'echo 3'}]}]}
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
            path = self._testfile(os.path.join('error', filename))

            with self.withAssertOutput('Reading file: %s\n' % path, '') as (out, err):
                self.assertRaisesRegexp(
                    ConfigError,
                    '^%s: %s$' % (path, expect),
                    lambda: Setting(config_path=path, stdout=out, stderr=err).load_config()
                )
