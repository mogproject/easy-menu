from __future__ import division, print_function, absolute_import, unicode_literals

import os
import sys
import re
import yaml
from six.moves.urllib.request import urlopen
from jinja2 import Environment
from mog_commons.command import capture_command
from mog_commons.string import *
from mog_commons.io import print_safe
from easy_menu.exceptions import ConfigError, EncodingError, SettingError

URL_PATTERN = re.compile(r'^http[s]?://')


class Loader(object):
    def __init__(self, work_dir, encoding='utf-8', stdout=sys.stdout):
        self.work_dir = work_dir
        self.encoding = encoding
        self.stdout = stdout
        self.cache = {}

    @staticmethod
    def is_url(path):
        return path is not None and bool(URL_PATTERN.match(path))

    def load(self, is_command, path_or_url_or_cmdline):
        """
        Load data from one file, url or command line, then store to a dict.

        :param is_command: True if using command line output
        :param path_or_url_or_cmdline:
        :return: dict representation of data
        """
        assert path_or_url_or_cmdline

        # normalize file path
        is_url = self.is_url(path_or_url_or_cmdline)
        if not is_command and not is_url:
            if self.work_dir is not None and not os.path.isabs(path_or_url_or_cmdline):
                path_or_url_or_cmdline = os.path.join(self.work_dir, path_or_url_or_cmdline)

        # if already loaded, use cache data
        c = self.cache.get((is_command, path_or_url_or_cmdline))
        if c is not None:
            return c

        try:
            if is_command:
                # execute command
                print_safe('Executing: %s' % path_or_url_or_cmdline, self.encoding, output=self.stdout)

                # ignore return code and stderr
                data = capture_command(path_or_url_or_cmdline, shell=True, cwd=self.work_dir,
                                       cmd_encoding=self.encoding)[1]
            elif self.is_url(path_or_url_or_cmdline):
                # read from URL
                print_safe('Reading from URL: %s' % path_or_url_or_cmdline, self.encoding, output=self.stdout)
                data = urlopen(path_or_url_or_cmdline).read()
            else:
                # read from file as bytes
                print_safe('Reading file: %s' % path_or_url_or_cmdline, self.encoding, output=self.stdout)
                with open(path_or_url_or_cmdline, 'rb') as f:
                    data = f.read()

            # decode string with fallback
            data_str = unicode_decode(data, [self.encoding, 'utf-8'])

            # apply jinja2 template rendering
            try:
                data_str = Environment().from_string(data_str).render()
            finally:
                pass

            # load as YAML string
            menu = yaml.load(data_str)

            # update cache data (Note: cache property is mutable!)
            self.cache[(is_command, path_or_url_or_cmdline)] = menu
        except IOError:
            raise ConfigError(path_or_url_or_cmdline, 'Failed to open.')
        except UnicodeDecodeError:
            raise EncodingError('Failed to decode with %s: %s' % (self.encoding, path_or_url_or_cmdline))
        except yaml.YAMLError as e:
            raise ConfigError(path_or_url_or_cmdline, 'YAML format error: %s' % to_unicode(str(e)))
        return menu
