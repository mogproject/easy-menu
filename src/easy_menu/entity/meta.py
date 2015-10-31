from __future__ import division, print_function, absolute_import, unicode_literals

import copy
import six
from mog_commons.case_class import CaseClass
from mog_commons.string import to_unicode, is_unicode, is_strlike


class Meta(CaseClass):
    """
    Meta settings for running commands
    """

    def __init__(self, work_dir=None, env=None):
        """
        :param work_dir:
        :param env:
        :return:
        """
        env = env or {}
        assert work_dir is None or is_unicode(work_dir)
        assert isinstance(env, dict) and all(is_unicode(k) and is_unicode(v) for k, v in env.items())

        CaseClass.__init__(self, ('work_dir', work_dir), ('env', env))

    def updated(self, data, encoding):
        """
        Load configuration and return updated instance.
        :param data: dict:
        :return: Meta:
        """
        assert isinstance(data, dict), 'Meta must be dist, not %s.' % type(data).__name__

        functions = {
            'work_dir': Meta._load_work_dir,
            'env': Meta._load_env
        }

        ret = self.copy()
        for k, v in data.items():
            ret = functions.get(k, self.__unknown_field(k))(ret, v, encoding)
        return ret

    def _load_work_dir(self, data, encoding):
        """Overwrite working directory"""
        assert is_strlike(data), 'work_dir must be string, not %s.' % type(data).__name__

        self.work_dir = to_unicode(data, encoding)
        return self

    def _load_env(self, data, encoding):
        """Merge environment variables"""
        assert isinstance(data, dict), 'env must be dict, not %s.' % type(data).__name__
        assert all(is_strlike(k) and is_strlike(v) for k, v in data.items()), \
            'env must be a dict of string key and string value.'

        d = copy.copy(self.env)
        d.update([(to_unicode(k, encoding), to_unicode(v, encoding)) for k, v in data.items()])
        self.env = d
        return self

    @staticmethod
    def __unknown_field(key):
        def f(x, y, z):
            raise ValueError('Unknown field: %s' % key)

        return f
