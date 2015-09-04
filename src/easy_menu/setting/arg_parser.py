from __future__ import division, print_function, absolute_import, unicode_literals

from optparse import OptionParser

VERSION = 'easy-menu %s' % __import__('easy_menu').__version__

USAGE = """%prog [options...] [<config_path> | <config_url>]"""


def __get_parser():
    p = OptionParser(version=VERSION, usage=USAGE)

    p.add_option(
        '--encode', dest='encoding', default=None, type='string', metavar='ENCODING',
        help='set output encoding to ENCODING'
    )

    p.add_option(
        '--lang', dest='lang', default=None, type='string', metavar='LANG',
        help='set language to LANG (in RFC 1766 format)'
    )

    p.add_option(
        '--width', dest='width', default=None, type='int', metavar='WIDTH',
        help='set window width to WIDTH'
    )

    p.add_option(
        '-d', '--work-dir', dest='work_dir', default=None, type='string', metavar='DIR',
        help='set working directory to DIR'
    )

    return p


parser = __get_parser()
