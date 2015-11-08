from __future__ import division, print_function, absolute_import, unicode_literals

from abc import ABCMeta, abstractmethod
import six


@six.add_metaclass(ABCMeta)
class Executor(object):
    """abstract executor class"""

    @abstractmethod
    def execute(self, command):
        """abstract method"""

    def is_running(self, command):
        """abstract method"""
