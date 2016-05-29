#!/Users/maciek/Repos/pwc/source/pwc/bin/python

import argparse
import logging

from utils.config import get_conf
from utils.log import get_log
from xml_parser import parse

CONF = get_conf()
LOG = get_log()


arg_parser = argparse.ArgumentParser(description='Parallel Wiki Classifier')

arg_parser.add_argument('--debug', default=False, action='store_true',
                        help='Forces log level to DEBUG')
arg_parser.add_argument('--parse', default=False, action='store_true',
                        help='Parse Wikipedia XML dump and load it do '
                             'database.')

args = arg_parser.parse_args()

if args.debug:
    LOG.setLevel(logging.DEBUG)

if args.parse:
    parse()
