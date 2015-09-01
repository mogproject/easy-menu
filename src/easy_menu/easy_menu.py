import sys
from view import Terminal
from controller import CommandExecutor
from setting.setting import Setting
from logger import SystemLogger
from util import network_util
from exceptions import EasyMenuError, InterruptError


def main():
    """
    Main function
    """

    try:
        setting = Setting().parse_args(sys.argv).lookup_config().load_meta().load_config()
        executor = CommandExecutor(setting.work_dir, SystemLogger())

        host = network_util.get_hostname()
        user = network_util.get_username()

        t = Terminal(setting.root_menu, host, user, executor, encoding=setting.encoding, lang=setting.lang)
        t.loop()
    except InterruptError:
        pass
    except EasyMenuError, e:
        print(e)
        return 2
    return 0
