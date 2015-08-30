from easy_menu.util import cmd_util


class CommandExecutor(object):
    def __init__(self, work_dir=None, logger=None):
        self.work_dir = work_dir
        self.logger = logger

    def execute(self, cmd, stdin, stdout, stderr):
        ret_code = cmd_util.execute_command(cmd, self.work_dir, stdin, stdout, stderr)

        # TODO: logging
        return ret_code
