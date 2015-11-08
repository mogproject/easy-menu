from __future__ import division, print_function, absolute_import, unicode_literals

import sys
import signal
import os
import socket
import getpass
from mog_commons.terminal import TerminalHandler
from easy_menu.view import Terminal
from easy_menu.controller import CommandExecutor
from easy_menu.setting.setting import Setting
from easy_menu.logger import SystemLogger
from easy_menu.exceptions import EasyMenuError


def get_hostname():
    hostname = socket.gethostname()
    nickname = os.environ.get('NICKNAME')
    return hostname + (' (%s)' % nickname if nickname else '')


def get_username():
    return getpass.getuser()


def main(stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr, keep_input_clean=True, timing=True):
    """
    Main function
    """

    base_setting = Setting(stdin=stdin, stdout=stdout, stderr=stderr).parse_args(sys.argv)

    # for terminal restoration
    handler = TerminalHandler(stdin=stdin, stdout=stdout, stderr=stderr,
                              keep_input_clean=keep_input_clean, getch_enabled=base_setting.getch_enabled)
    signal.signal(signal.SIGTERM, handler.restore_terminal)

    try:
        setting = base_setting.resolve_encoding(handler).lookup_config().load_config()
        executor = CommandExecutor(
            SystemLogger(setting.encoding), setting.encoding, stdin, stdout, stderr, setting.pid_dir
        )

        t = Terminal(
            setting.root_menu,
            get_hostname(),
            get_username(),
            executor,
            handler=handler,
            _input=setting.stdin,
            _output=setting.stdout,
            encoding=setting.encoding,
            lang=setting.lang,
            width=setting.width,
            timing=timing
        )

        t.loop()
    except (KeyboardInterrupt, EOFError):
        pass
    except EasyMenuError as e:
        base_setting.stdout.write('%s: %s\n' % (e.__class__.__name__, e))
        return 2
    except IOError as e:
        # maybe killed by outside
        base_setting.stdout.write('\n%s: %s\n' % (e.__class__.__name__, e))
        return 3
    except OSError as e:
        # e.g. working directory does not exist
        base_setting.stdout.write('%s: %s\n' % (e.__class__.__name__, e))
        return 4
    finally:
        # assume to restore original terminal settings
        handler.restore_terminal(None, None)
    return 0
