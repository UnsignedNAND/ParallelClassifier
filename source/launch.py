#!/usr/bin/python

import argparse

from parser import parse as parse_wiki

arg_parser = argparse.ArgumentParser(description='Parallel Wiki Classifier')
arg_parser.add_argument('--parse', default=False, action='store_true',
                        help='Parse Wikipedia XML dump and load it do database.')
arg_parser.add_argument('--process', default=False, action='store_true',
                        help='Process text documents stored in database.')
arg_parser.add_argument('--delete', default=False, action='store_true',
                        help='Delete all data from database upon start.')

args = arg_parser.parse_args()

print args

if not(args.parse or args.process):
    print 'Supply at least one action.'
    arg_parser.print_help()
    exit()

if args.delete:
    pass

if args.parse:
    parse_wiki()

if args.process:
    pass
