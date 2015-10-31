# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import os
import six
from mog_commons.unittest import TestCase, base_unittest
from mog_commons.string import to_unicode
from easy_menu.setting.setting import Setting
from easy_menu.entity import Menu, Command, CommandLine, Meta
from easy_menu.exceptions import ConfigError, SettingError, EncodingError


class TestSetting(TestCase):
    def _testfile(self, filename):
        return os.path.join(os.path.abspath(os.path.curdir), 'tests', 'resources', filename)

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

    def test_resolve_encoding(self):
        import io
        import codecs

        if six.PY2:
            out = codecs.getwriter('sjis')
            out.encoding = 'sjis'
        else:
            out = io.TextIOWrapper(six.StringIO(), 'sjis')

        self.assertEqual(Setting(stdout=out).resolve_encoding().encoding, 'sjis')
        self.assertEqual(Setting(encoding='utf-8', stdout=out).resolve_encoding().encoding, 'utf-8')

    def test_find_lang(self):
        s = Setting()
        old = os.environ.get('LANG')

        if old:
            del os.environ['LANG']
        self.assertEqual(s._find_lang('ja_JP'), 'ja_JP')
        s._find_lang(None)  # return value depends on the system

        os.environ['LANG'] = 'en_US'
        self.assertEqual(s._find_lang(None), 'en_US')

        if old:
            os.environ['LANG'] = old

    @base_unittest.skipUnless(os.name != 'nt', 'requires POSIX compatible')
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

        with self.withAssertOutput(expect_stdout, '') as (out, err):
            self.assertSystemExit(2, Setting(stdout=out, stderr=err).parse_args, ['easy-menu', 'a', 'b'])

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

    def test_load_config(self):
        meta = Meta(to_unicode(os.path.join(os.path.abspath(os.path.curdir), 'tests', 'resources')))

        with self.withAssertOutput('Reading file: %s\n' % self._testfile('minimum.yml'), '') as (out, err):
            self.assertEqual(
                Setting(
                    config_path=self._testfile('minimum.yml'), encoding='utf-8', stdout=out, stderr=err
                ).load_config().root_menu,
                Menu('', [], meta)
            )
        path = os.path.join(os.path.abspath(os.path.curdir), 'tests', 'resources', 'flat.yml')
        with self.withAssertOutput('Reading file: %s\n' % path, '') as (out, err):
            self.assertEqual(
                Setting(
                    config_path=self._testfile('flat.yml'), encoding='utf-8', stdout=out, stderr=err
                ).load_config().root_menu,
                Menu('Main Menu', [
                    Command('Menu 1', [CommandLine('echo 1', meta)]),
                    Command('Menu 2', [CommandLine('echo 2', meta)]),
                    Command('Menu 3', [CommandLine('echo 3', meta)]),
                    Command('Menu 4', [CommandLine('echo 4', meta)]),
                    Command('Menu 5', [CommandLine('echo 5', meta)]),
                    Command('Menu 6', [CommandLine('echo 6', meta)]),
                ], meta)
            )

    @base_unittest.skipUnless(os.name != 'nt', 'requires POSIX compatible')
    def test_load_config_dynamic(self):
        meta = Meta(to_unicode(os.path.join(os.path.abspath(os.path.curdir), 'tests', 'resources')))
        path = os.path.join(os.path.abspath(os.path.curdir), 'tests', 'resources', 'with_dynamic.yml')
        expect = '\n'.join([
            'Reading file: %s' % path,
            """Executing: echo '{"Sub Menu": [{"Menu 2": "echo 2"}, {"Menu 3": "echo 3"}]}'\n"""
        ])
        with self.withAssertOutput(expect, '') as (out, err):
            self.assertEqual(
                Setting(
                    config_path=self._testfile('with_dynamic.yml'), encoding='utf-8', stdout=out, stderr=err
                ).load_config().root_menu,
                Menu('Main Menu', [
                    Command('Menu 1', [CommandLine('echo 1', meta)]),
                    Menu('Sub Menu', [
                        Command('Menu 2', [CommandLine('echo 2', meta)]),
                        Command('Menu 3', [CommandLine('echo 3', meta)]),
                    ], meta)
                ], meta)
            )

    def test_load_config_error_not_found(self):
        self.assertRaisesMessage(
            SettingError,
            'Not found configuration file.',
            Setting().load_config
        )

    def test_load_config_error(self):
        self.maxDiff = None

        inputs = [
            ('error_not_exist.yml', 'Failed to open.'),
            ('error_parser.yml', 'YAML format error: expected \'<document start>\', but found \'<scalar>\'\n'
                                 '  in "<unicode string>", line 1, column 3:\n    \'\':1\n      ^'),
            ('error_scanner.yml',
             'YAML format error: while scanning a quoted scalar\n  in "<unicode string>", line 1, column 1:\n    "'
             '\n    ^\nfound unexpected end of stream\n  in "<unicode string>", line 1, column 2:\n    "\n     ^'),
            ('error_parser_utf8_ja.yml', 'YAML format error: while parsing a flow mapping\n'
                                         '  in "<unicode string>", line 1, column 1:\n'
                                         '    {\n'
                                         '    ^\n'
                                         "expected ',' or '}', but got '<scalar>'\n"
                                         '  in "<unicode string>", line 3, column 7:\n'
                                         """        {"サービス稼動状態確認": "echo 'サービス稼動状態確認'"},\n"""
                                         '          ^'),
            ('error_command_only.yml', 'Menu content must be list, not str.'),
            ('error_include_as_submenu.yml', '"include" section must have string content, not list.'),
            ('error_dynamic_as_submenu.yml', '"eval" section must have string content, not list.'),
            ('error_include_loop.yml', 'Nesting level too deep.'),
            ('error_key_only1.yml', 'Menu content must be list, not NoneType.'),
            ('error_key_only2.yml', 'Menu content must be list, not NoneType.'),
            ('error_meta_only.yml', 'Menu should have only one item, not 0.'),
            ('error_multiple_items.yml', 'Menu should have only one item, not 2.'),
            ('error_not_dict1.yml', 'Menu must be dict, not list.'),
            ('error_not_dict2.yml', 'Item must be dict, not int.'),
        ]

        for filename, expect in inputs:
            path = self._testfile(os.path.join('error', filename))
            with self.withAssertOutput('Reading file: %s\n' % path, '') as (out, err):
                self.assertRaisesMessage(
                    ConfigError,
                    '%s: %s' % (path, expect),
                    Setting(config_path=path, stdout=out, stderr=err, encoding='utf-8').load_config)

    def test_load_config_error_sjis(self):
        self.maxDiff = None

        inputs = [
            ('error_parser_sjis_ja.yml', 'YAML format error: while parsing a flow mapping\n'
                                         '  in "<unicode string>", line 1, column 1:\n'
                                         '    {\n'
                                         '    ^\n'
                                         "expected ',' or '}', but got '<scalar>'\n"
                                         '  in "<unicode string>", line 3, column 7:\n'
                                         """        {"サービス稼動状態確認": "echo 'サービス稼動状態確認'"},\n"""
                                         '          ^'),
        ]

        for filename, expect in inputs:
            path = self._testfile(os.path.join('error', filename))
            with self.withAssertOutput('Reading file: %s\n' % path, '', 'sjis') as (out, err):
                self.assertRaisesMessage(
                    ConfigError,
                    '%s: %s' % (path, expect),
                    Setting(config_path=path, stdout=out, stderr=err, encoding='sjis').load_config)

    def test_load_data_encoding_error_file(self):
        path = self._testfile('sjis_ja.yml')
        with self.withAssertOutput('Reading file: %s\n' % path, '') as (out, err):
            self.assertRaisesMessage(
                EncodingError,
                'Failed to decode with utf-8: %s' % path,
                Setting(config_path=path, encoding='utf-8', stdout=out, stderr=err).load_config
            )
