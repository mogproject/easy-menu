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

from mog_commons.string import to_unicode, is_unicode

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


def restore_term_func(_input=sys.stdin):
    assert hasattr(_input, 'fileno'), 'Invalid input device.'

    if os.name == 'nt':
        return lambda signal, frame: None
    fd = _input.fileno()
    try:
        original_settings = termios.tcgetattr(fd)
    except termios.error:
        return lambda signal, frame: None
    return lambda signal, frame: termios.tcsetattr(fd, termios.TCSADRAIN, original_settings)


def getch(_input=sys.stdin):
    """Wait and get one character from input"""

    global LAST_GETCH_TIME
    global LAST_GETCH_CHAR

    if os.name == 'nt':
        ch = msvcrt.getch()
    else:
        ch = _wrap_termios(_input, lambda: _input.read(1))

    try:
        uch = to_unicode(ch, 'ascii')
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
