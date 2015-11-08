from __future__ import division, print_function, absolute_import, unicode_literals

from mog_commons.types import *
from easy_menu.controller.executor import Executor


class MockExecutor(Executor):
    @types(return_code=int, is_running=bool)
    def __init__(self, return_code, is_running):
        self._return_code = return_code
        self._is_running = is_running

    def execute(self, command):
        return self._return_code

    def is_running(self, command):
        return self._is_running
