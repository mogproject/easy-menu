from optparse import OptionParser

VERSION = 'easy-menu %s' % __import__('easy_menu').__version__

USAGE = """
%prog [options] [CONFIG_PATH | CONFIG_URL]"""


def __get_parser():
    p = OptionParser(version=VERSION, usage=USAGE)

    p.add_option(
        '--encode', dest='encoding', default=None, type='string', metavar='ENCODING',
        help='set output encoding to ENCODING'
    )

    return p


parser = __get_parser()
