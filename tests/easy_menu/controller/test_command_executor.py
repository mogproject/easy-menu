from __future__ import division, print_function, absolute_import, unicode_literals

import time
import tempfile
import threading
import sys
import os
from mog_commons.unittest import TestCase
from easy_menu.controller import CommandExecutor
from easy_menu.entity import Command, CommandLine, Meta
from tests.easy_menu.logger.mock_logger import MockLogger


class TestCommandExecutor(TestCase):
    def test_is_running(self):
        tempdir = tempfile.mkdtemp()
        try:
            sleep_cmd = 'python -c "import time;time.sleep(1)"' if os.name == 'nt' else 'sleep 1'
            cmd = Command('cmd 1', [
                CommandLine(sleep_cmd, Meta(lock=True)),
                CommandLine(sleep_cmd, Meta(lock=True)),
            ])

            exe = CommandExecutor(MockLogger(), 'utf-8', sys.stdin, sys.stdout, sys.stderr, tempdir)

            class RunSleep(threading.Thread):
                def run(self):
                    exe.execute(cmd)

            th = RunSleep()
            th.start()
            time.sleep(0.5)

            self.assertTrue(exe.is_running(cmd))
            time.sleep(1)
            self.assertTrue(exe.is_running(cmd))
            time.sleep(1)
            self.assertFalse(exe.is_running(cmd))
        finally:
            for child in os.listdir(tempdir):
                os.removedirs(os.path.join(tempdir, child))
            if os.path.exists(tempdir):
                os.removedirs(tempdir)
