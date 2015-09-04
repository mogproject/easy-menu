from __future__ import division, print_function, absolute_import, unicode_literals

import sys
from easy_menu.view import Terminal
from easy_menu.controller import CommandExecutor
from easy_menu.setting.setting import Setting
from easy_menu.logger import SystemLogger
from easy_menu.util import network_util
from easy_menu.exceptions import EasyMenuError, InterruptError


def main():
    """
    Main function
    """

    try:
        setting = Setting().parse_args(sys.argv).lookup_config().load_meta().load_config()
        executor = CommandExecutor(setting.work_dir, SystemLogger())

        host = network_util.get_hostname()
        user = network_util.get_username()

        t = Terminal(setting.root_menu, host, user, executor, encoding=setting.encoding, lang=setting.lang,
                     width=setting.width)
        t.loop()
    except InterruptError:
        pass
    except (EasyMenuError, AssertionError) as e:
        print('%s: %s' % (e.__class__.__name__, e))
        return 2
    return 0
