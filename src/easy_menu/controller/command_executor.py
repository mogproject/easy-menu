import subprocess


class CommandExecutor(object):
    def __init__(self, work_dir=None, logger=None):
        self.work_dir = work_dir
        self.logger = logger

    def execute(self, command_str, stdin, stdout, stderr):
        try:
            ret_code = subprocess.call(
                command_str,
                shell=True,
                stdin=stdin,
                stdout=stdout,
                stderr=stderr,
                cwd=self.work_dir,
            )
        except KeyboardInterrupt:
            ret_code = 130

        # TODO: logging
        return ret_code
