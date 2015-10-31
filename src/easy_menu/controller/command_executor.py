from __future__ import division, print_function, absolute_import, unicode_literals

from mog_commons.command import execute_command
from easy_menu.entity.command import Command
from easy_menu.logger.logger import Logger


class CommandExecutor(object):
    def __init__(self, logger, encoding, stdin, stdout, stderr):
        assert isinstance(logger, Logger)

        self.logger = logger
        self.encoding = encoding
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    def execute(self, command):
        assert isinstance(command, Command)

        ret_code = 0
        for command_line in command.command_lines:
            try:
                self.logger.info('Command started: %s' % command_line.cmd)
                ret_code = execute_command(command_line.cmd, shell=True,
                                           cwd=command_line.meta.work_dir, env=command_line.meta.env,
                                           stdin=self.stdin, stdout=self.stdout, stderr=self.stderr,
                                           cmd_encoding=self.encoding)
                self.logger.info('Command ended with return code: %d' % ret_code)

            except KeyboardInterrupt:
                self.logger.info('Command interrupted.')
                ret_code = 130

            # if a command fails, the successors will not run
            if ret_code != 0:
                break
        return ret_code
