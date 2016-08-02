#!/Users/maciek/Repos/pwc/source/pwc/bin/python

import argparse
import logging

from data.db import Db
from parsing.wiki_parser import parse, distance, cluster
from utils.config import get_conf
from utils.log import get_log

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
    '--features',
    default=False,
    action='store_true',
    help='Extract features from articles'
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

args = arg_parser.parse_args()

if args.debug:
    LOG.setLevel(logging.DEBUG)

if args.clean:
    Db.clean()

if args.parse:
    parse()

if args.features:
    pass

if args.distance:
    distance()

if args.cluster:
    cluster()
