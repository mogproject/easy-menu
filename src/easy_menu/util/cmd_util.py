from __future__ import division, print_function, absolute_import, unicode_literals

import sys
import subprocess
from easy_menu.util import string_util

# Note: workaround for http://bugs.python.org/issue8513
NOT_USE_SHELL = sys.version_info[:2] == (3, 2) and not sys.platform == 'win32'


def execute_command(cmd, work_dir, stdin, stdout, stderr, encoding='utf-8'):
    """
    Execute external command

    :param cmd: command line string
    :param work_dir: working directory
    :param stdin: standard input
    :param stdout: standard output
    :param stderr: standard error
    :return: return code
    """
    assert string_util.is_unicode(cmd), 'cmd must be unicode string, not %s' % type(cmd).__name__

    try:
        if NOT_USE_SHELL:
            ret_code = subprocess.call(
                ['/bin/sh', '-c', cmd.encode(encoding)],
                shell=False,
                stdin=stdin,
                stdout=stdout,
                stderr=stderr,
                cwd=work_dir,
            )
        else:
            ret_code = subprocess.call(
                cmd.encode(encoding),
                shell=True,
                stdin=stdin,
                stdout=stdout,
                stderr=stderr,
                cwd=work_dir,
            )
    except KeyboardInterrupt:
        ret_code = 130

    return ret_code


def capture_command(cmd, work_dir, stdin=sys.stdin, encoding='utf-8'):
    """
    Execute external command and capture output

    :param cmd: command line string
    :param work_dir: working directory
    :param stdin: standard input
    :return: tuple of return code, stdout data and stderr data
    """
    assert string_util.is_unicode(cmd), 'cmd must be unicode string, not %s' % type(cmd).__name__

    stdout_data, stderr_data = None, None

    try:
        if NOT_USE_SHELL:
            p = subprocess.Popen(
                ['/bin/sh', '-c', cmd.encode(encoding)],
                shell=False,
                stdin=stdin,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=work_dir
            )
        else:
            p = subprocess.Popen(
                cmd.encode(encoding),
                shell=True,
                stdin=stdin,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=work_dir
            )
        stdout_data, stderr_data = p.communicate()
        ret_code = p.returncode
    except KeyboardInterrupt:
        ret_code = 130

    return ret_code, stdout_data, stderr_data
