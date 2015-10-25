from __future__ import division, print_function, absolute_import, unicode_literals

from mog_commons.command import execute_command


class CommandExecutor(object):
    def __init__(self, work_dir=None, logger=None):
        self.work_dir = work_dir
        self.logger = logger

    def execute(self, cmd, stdin, stdout, stderr, encoding):
        self.logger.info('Command started: %s' % cmd)
        try:
            ret_code = execute_command(cmd, shell=True, cwd=self.work_dir,
                                       stdin=stdin, stdout=stdout, stderr=stderr, cmd_encoding=encoding)
            self.logger.info('Command ended with return code: %d' % ret_code)
        except KeyboardInterrupt:
            self.logger.info('Command interrupted.')
            ret_code = 130

        return ret_code
