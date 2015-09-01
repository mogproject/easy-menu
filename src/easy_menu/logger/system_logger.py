from __future__ import division, print_function, absolute_import, unicode_literals

import os
import sys
import syslog
from easy_menu.logger.logger import Logger


class SystemLogger(Logger):
    def __init__(self):
        self.name = os.path.basename(sys.argv[0])
        super(SystemLogger, self).__init__('SystemLogger[%s]' % self.name)

    def _log(self, priority, message):
        syslog.openlog(self.name, syslog.LOG_PID)
        syslog.syslog(priority, message)
        syslog.closelog()
