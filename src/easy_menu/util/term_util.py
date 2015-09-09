from __future__ import division, print_function, absolute_import, unicode_literals

import sys
import os
import time
import subprocess

if os.name == 'nt':
    # for Windows
    import msvcrt
else:
    # for Unix/Linux/Mac
    import termios
    import tty

from easy_menu.util import string_util

LAST_GETCH_TIME = 0.0
LAST_GETCH_CHAR = ''


def _wrap_termios(_input, func):
    assert hasattr(_input, 'fileno'), 'Invalid input device.'

    fd = _input.fileno()
    old_settings = None
    try:
        try:
            old_settings = termios.tcgetattr(fd)
            tty.setraw(fd)
        except termios.error:
            pass
        ret = func()
    finally:
        if old_settings:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return ret


def getch(_input=sys.stdin):
    """Wait and get one character from input"""

    global LAST_GETCH_TIME
    global LAST_GETCH_CHAR

    if os.name == 'nt':
        ch = msvcrt.getch()
    else:
        ch = _wrap_termios(_input, lambda: _input.read(1))

    try:
        uch = string_util.to_unicode(ch, 'ascii')
    except UnicodeError:
        return ''

    t = time.time()

    # check key repeat
    if LAST_GETCH_CHAR == uch:
        if t < LAST_GETCH_TIME + 0.3:
            LAST_GETCH_TIME = t
            return ''

    LAST_GETCH_TIME = t
    LAST_GETCH_CHAR = uch

    return uch


def clear_screen(_input=sys.stdin, _output=sys.stdout):
    """Clear terminal screen."""

    if not _output.isatty():
        return

    cmd = 'cls' if os.name == 'nt' else 'clear'
    subprocess.call(cmd, shell=True, stdin=_input, stdout=_output, stderr=_output)


def universal_print(output, str_or_bytes, encoding='utf-8'):
    """Print unicode or bytes universally"""

    if string_util.is_unicode(str_or_bytes):
        bs = str_or_bytes.encode(encoding)
    else:
        bs = str_or_bytes

    if hasattr(output, 'buffer'):
        output.buffer.write(bs)
    else:
        try:
            output.write(bs)
        except TypeError:
            output.write(str_or_bytes)

    output.flush()
