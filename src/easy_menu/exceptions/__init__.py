class EncodeError(Exception):
    """Encode error."""

    def __init__(self, msg=''):
        super(self, EncodeError).__init__('Encode error: %s' % msg)


class InterruptError(Exception):
    """Interruption error."""


class SettingError(Exception):
    """Setting error."""
