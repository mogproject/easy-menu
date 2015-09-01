from __future__ import division, print_function, absolute_import, unicode_literals

import syslog
from abc import ABCMeta, abstractmethod
import six
from easy_menu.util import CaseClass


@six.add_metaclass(ABCMeta)
class Logger(CaseClass):
    """abstract logger class"""

    def __init__(self, ident):
        """
        :param ident: identity for logger
        """
        CaseClass.__init__(self, ('ident', ident))

    def info(self, message):
        self._log_message(syslog.LOG_INFO, message)

    def warn(self, message):
        self._log_message(syslog.LOG_WARNING, message)

    def error(self, message):
        self._log_message(syslog.LOG_ERR, message)

    def traceback(self):
        """do nothing by default"""

    def _log_message(self, priority, message):
        prefix = {
            syslog.LOG_INFO: '[INFO] ',
            syslog.LOG_WARNING: '[WARN] ',
            syslog.LOG_ERR: '[ERROR]'
        }[priority]
        msg = '%s%s' % (prefix, message)
        self._log(priority, msg)

    @abstractmethod
    def _log(self, priority, message):
        """log raw message"""
