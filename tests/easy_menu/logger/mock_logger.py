from easy_menu.logger.logger import Logger


class MockLogger(Logger):
    def __init__(self):
        Logger.__init__(self, 'MockLogger')
        self.buffer = []

    def _log(self, priority, message):
        self.buffer.append((priority, message))
