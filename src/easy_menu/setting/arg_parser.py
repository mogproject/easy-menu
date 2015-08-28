from optparse import OptionParser

VERSION = 'easy-menu %s' % __import__('easy_menu').__version__

USAGE = """
%prog [options] [CONFIG_PATH | CONFIG_URL]"""


def __get_parser():
    p = OptionParser(version=VERSION, usage=USAGE)

    return p


parser = __get_parser()
