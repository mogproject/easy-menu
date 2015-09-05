from __future__ import division, print_function, absolute_import, unicode_literals


class EasyMenuError(Exception):
    """Base class of application specific exceptions"""


class EncodingError(EasyMenuError):
    """Encode error."""


class SettingError(EasyMenuError):
    """Setting error."""


class ConfigError(EasyMenuError):
    """Configuration error."""

    def __init__(self, path, msg=''):
        EasyMenuError.__init__(self, '%s: %s' % (path, msg))
