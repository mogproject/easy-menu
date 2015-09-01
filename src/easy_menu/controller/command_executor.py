from easy_menu.util import cmd_util


class CommandExecutor(object):
    def __init__(self, work_dir=None, logger=None):
        self.work_dir = work_dir
        self.logger = logger

    def _log_info(self, msg):
        if self.logger:
            self.logger.info(msg)

    def execute(self, cmd, stdin, stdout, stderr):
        self._log_info('Command started: %s' % cmd)
        ret_code = cmd_util.execute_command(cmd, self.work_dir, stdin, stdout, stderr)
        self._log_info('Command ended with return code: %d' % ret_code)
        return ret_code
