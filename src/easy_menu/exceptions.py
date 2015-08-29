class EasyMenuError(Exception):
    """Base class of application specific exceptions"""


class EncodeError(EasyMenuError):
    """Encode error."""

    def __init__(self, msg=''):
        super(self, EncodeError).__init__('Encode error: %s' % msg)


class InterruptError(EasyMenuError):
    """Interruption error."""


class SettingError(EasyMenuError):
    """Setting error."""


class ConfigError(EasyMenuError):
    """Configuration error."""
