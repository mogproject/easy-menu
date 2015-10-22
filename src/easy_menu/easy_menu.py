from __future__ import division, print_function, absolute_import, unicode_literals

import sys
import signal
from easy_menu.view import Terminal
from easy_menu.controller import CommandExecutor
from easy_menu.setting.setting import Setting
from easy_menu.logger import SystemLogger
from easy_menu.util import network_util, term_util
from easy_menu.exceptions import EasyMenuError


def main(stdin=None, stdout=None, stderr=None):
    """
    Main function
    """

    # for terminal restoration
    restore_term_func = term_util.restore_term_func(sys.stdin)
    signal.signal(signal.SIGTERM, restore_term_func)

    base_setting = Setting(stdin=stdin, stdout=stdout, stderr=stderr)

    try:
        setting = base_setting.parse_args(sys.argv).resolve_encoding().lookup_config().load_meta().load_config()
        executor = CommandExecutor(setting.work_dir, SystemLogger(setting.encoding))

        t = Terminal(
            setting.root_menu,
            network_util.get_hostname(),
            network_util.get_username(),
            executor,
            _input=setting.stdin,
            _output=setting.stdout,
            encoding=setting.encoding,
            lang=setting.lang,
            width=setting.width
        )

        t.loop()
    except KeyboardInterrupt:
        pass
    except EasyMenuError as e:
        base_setting.stdout.write('%s: %s\n' % (e.__class__.__name__, e))
        return 2
    except IOError as e:
        # maybe killed by outside
        base_setting.stdout.write('\n%s: %s\n' % (e.__class__.__name__, e))
        return 3
    finally:
        # assume to restore original terminal settings
        restore_term_func(None, None)
    return 0
