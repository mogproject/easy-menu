from __future__ import division, print_function, absolute_import, unicode_literals

import copy
from mog_commons.case_class import CaseClass
from mog_commons.types import *
from mog_commons.string import to_unicode


class Meta(CaseClass):
    """
    Meta settings for running commands
    """

    @types(work_dir=Option(Unicode), env=Option(DictOf(Unicode, Unicode)), lock=bool)
    def __init__(self, work_dir=None, env=None, lock=False):
        """
        :param work_dir:
        :param env:
        :param lock:
        :return:
        """
        env = env or {}
        CaseClass.__init__(self, ('work_dir', work_dir), ('env', env), ('lock', lock))

    @types(data=dict)
    def updated(self, data, encoding):
        """
        Load configuration and return updated instance.
        :param data: dict:
        :return: Meta:
        """
        functions = {
            'work_dir': Meta._load_work_dir,
            'env': Meta._load_env,
            'lock': Meta._load_lock,
        }

        ret = self.copy()
        for k, v in data.items():
            ret = functions.get(k, self.__unknown_field(k))(ret, v, encoding)
        return ret

    @types(data=String, encoding=String)
    def _load_work_dir(self, data, encoding):
        """Overwrite working directory"""
        self.work_dir = to_unicode(data, encoding)
        return self

    @types(data=DictOf(String, String), encoding=String)
    def _load_env(self, data, encoding):
        """Merge environment variables"""
        d = copy.copy(self.env)
        d.update([(to_unicode(k, encoding), to_unicode(v, encoding)) for k, v in data.items()])
        self.env = d
        return self

    @types(data=bool, encoding=String)
    def _load_lock(self, data, encoding):
        """Overwrite lock setting"""
        self.lock = data
        return self

    @staticmethod
    def __unknown_field(key):
        def f(x, y, z):
            raise ValueError('Unknown field: %s' % key)

        return f
