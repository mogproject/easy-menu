from __future__ import division, print_function, absolute_import, unicode_literals

import os
from mog_commons.command import execute_command_with_pid, pid_exists
from mog_commons.types import *
from easy_menu.entity.command import Command, CommandLine
from easy_menu.logger.logger import Logger
from easy_menu.controller.executor import Executor


class CommandExecutor(Executor):
    @types(logger=Logger)
    def __init__(self, logger, encoding, stdin, stdout, stderr, pid_dir):
        self.logger = logger
        self.encoding = encoding
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pid_dir = pid_dir

    @types(int, command=Command)
    def execute(self, command):
        ret_code = 0
        for command_line in command.command_lines:
            try:
                self.logger.info('Command started: %s' % command_line.cmd)
                if command_line.meta.lock:
                    pid_file = self._pid_file_path(command_line)

                    # create pid directory
                    if not os.path.exists(os.path.dirname(pid_file)):
                        os.makedirs(os.path.dirname(pid_file))
                else:
                    pid_file = None

                ret_code = execute_command_with_pid(
                    command_line.cmd, pid_file=pid_file, shell=True, cwd=command_line.meta.work_dir,
                    env=command_line.meta.env, stdin=self.stdin, stdout=self.stdout, stderr=self.stderr,
                    cmd_encoding=self.encoding)
                self.logger.info('Command ended with return code: %d' % ret_code)

            except KeyboardInterrupt:
                self.logger.info('Command interrupted.')
                ret_code = 130

            # if a command fails, the successors will not run
            if ret_code != 0:
                break
        return ret_code

    @types(bool, command=Command)
    def is_running(self, command):
        def check_pid(cmdline):
            if not cmdline.meta.lock:
                return False

            path = self._pid_file_path(cmdline)
            if not os.path.exists(path):
                return False

            with open(path, 'r') as f:
                pid = int(f.read())
            return pid_exists(pid)

        return any(check_pid(c) for c in command.command_lines)

    @types(String, cmdline=CommandLine)
    def _pid_file_path(self, cmdline):
        h = cmdline.to_hash_string()
        return os.path.join(self.pid_dir, h[:2], h[2:])
