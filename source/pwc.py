#!/Users/maciek/Repos/pwc/source/pwc/bin/python

import argparse
import logging

from data.db import Db
from core.main import parse, distance, cluster, classify
from utils.config import get_conf
from utils.log import get_log
from utils.timer import timer

CONF = get_conf()
LOG = get_log()

try:
    Db.init()
except Exception as ex:
    LOG.error(ex)
    exit()


arg_parser = argparse.ArgumentParser(description='Parallel Wiki Classifier')

arg_parser.add_argument(
    '--debug',
    default=False,
    action='store_true',
    help='Forces log level to DEBUG'
)
arg_parser.add_argument(
    '--no-debug',
    default=False,
    action='store_true',
    help='Forces log level to INFO'
)
arg_parser.add_argument(
    '--clean',
    default=False,
    action='store_true',
    help='Wipe out all data stored in database'
)
arg_parser.add_argument(
    '--parse',
    default=False,
    action='store_true',
    help='Parse Wikipedia XML dump and load it do database.'
)

arg_parser.add_argument(
    '--distance',
    default=False,
    action='store_true',
    help='Count distance between articles'
)

arg_parser.add_argument(
    '--cluster',
    default=False,
    action='store_true',
    help='Divide documents into clusters'
)

arg_parser.add_argument(
    '--classify',
    default=False,
    action='store_true',
    help='Classificate new documents using kNN algorithm'
)

args = arg_parser.parse_args()


@timer
def process():
    if args.debug:
        LOG.setLevel(logging.DEBUG)

    if args.no_debug:
        LOG.setLevel(logging.INFO)

    if args.clean:
        Db.clean()

    if args.parse:
        parse()

    if args.distance:
        distance()

    if args.cluster:
        cluster()

    if args.classify:
        classify()

if __name__ == '__main__':
    process()
