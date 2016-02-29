#!/usr/bin/python

import argparse

from compute.receiver import receive


arg_parser = argparse.ArgumentParser(description='Parallel Wiki Classifier')
arg_parser.add_argument('--process', default=False, action='store_true',
                        help='Process text documents stored in database.')

args = arg_parser.parse_args()

print args

if not args.process:
    print 'Supply at least one action.'
    arg_parser.print_help()
    exit()

if args.process:
    receive()
