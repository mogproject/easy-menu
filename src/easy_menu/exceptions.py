from __future__ import division, print_function, absolute_import, unicode_literals


class EasyMenuError(Exception):
    """Base class of application specific exceptions"""


class EncodeError(EasyMenuError):
    """Encode error."""

    def __init__(self, msg=''):
        EasyMenuError.__init__(self, 'Encode error: %s' % msg)


class InterruptError(EasyMenuError):
    """Interruption error."""


class SettingError(EasyMenuError):
    """Setting error."""


class ConfigError(EasyMenuError):
    """Configuration error."""

    def __init__(self, path, msg=''):
        EasyMenuError.__init__(self, 'Configuration error: %s: %s' % (path, msg))
