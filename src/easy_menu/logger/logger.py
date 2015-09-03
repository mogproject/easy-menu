from __future__ import division, print_function, absolute_import, unicode_literals

from abc import ABCMeta, abstractmethod
import six
from easy_menu.util import CaseClass

# copied from syslog module
LOG_ALERT = 1
LOG_AUTH = 32
LOG_CONS = 2
LOG_CRIT = 2
LOG_CRON = 72
LOG_DAEMON = 24
LOG_DEBUG = 7
LOG_EMERG = 0
LOG_ERR = 3
LOG_INFO = 6
LOG_KERN = 0
LOG_LOCAL0 = 128
LOG_LOCAL1 = 136
LOG_LOCAL2 = 144
LOG_LOCAL3 = 152
LOG_LOCAL4 = 160
LOG_LOCAL5 = 168
LOG_LOCAL6 = 176
LOG_LOCAL7 = 184
LOG_LPR = 48
LOG_MAIL = 16
LOG_NDELAY = 8
LOG_NEWS = 56
LOG_NOTICE = 5
LOG_NOWAIT = 16
LOG_PERROR = 32
LOG_PID = 1
LOG_SYSLOG = 40
LOG_USER = 8
LOG_UUCP = 64
LOG_WARNING = 4


@six.add_metaclass(ABCMeta)
class Logger(CaseClass):
    """abstract logger class"""

    def __init__(self, ident):
        """
        :param ident: identity for logger
        """
        CaseClass.__init__(self, ('ident', ident))

    def info(self, message):
        self._log_message(LOG_INFO, message)

    def warn(self, message):
        self._log_message(LOG_WARNING, message)

    def error(self, message):
        self._log_message(LOG_ERR, message)

    def traceback(self):
        """do nothing by default"""

    def _log_message(self, priority, message):
        prefix = {
            LOG_INFO: '[INFO] ',
            LOG_WARNING: '[WARN] ',
            LOG_ERR: '[ERROR]'
        }[priority]
        msg = '%s%s' % (prefix, message)
        self._log(priority, msg)

    @abstractmethod
    def _log(self, priority, message):
        """log raw message"""
