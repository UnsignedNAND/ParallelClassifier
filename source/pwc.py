#!/Users/maciek/Repos/pwc/source/pwc/bin/python

import argparse
import logging

from data.db import Db
from core.main import Main
from utils.config import get_conf
from utils.log import get_log
from utils.timer import timer, time_records


class ParallelWikiClassifier(object):
    args = None

    def __init__(self):
        self.log = get_log()
        self._init_db()
        self._parse_args()

    def _init_db(self):
        global Db
        try:
            Db.init()
        except Exception as ex:
            self.log.error(ex)
            exit()

    def _parse_args(self):
        arg_parser = argparse.ArgumentParser(description='Parallel Wiki '
                                                         'Classifier')
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

        arg_parser.add_argument(
            '--svm',
            default=False,
            action='store_true',
            help='Classificate new documents using SVM algorithm'
        )

        self.args = arg_parser.parse_args()


    @timer
    def process(self):
        global Db
        main = Main()
        if self.args.debug:
            self.log.setLevel(logging.DEBUG)

        if self.args.no_debug:
            self.log.setLevel(logging.INFO)

        if self.args.clean:
            Db.clean()

        if self.args.parse:
            main.parse()

        if self.args.distance:
            main.distance()

        if self.args.cluster:
            main.cluster()

        if self.args.classify:
            main.classify()

        if self.args.svm:
            main.classify_svm()

if __name__ == '__main__':
    main = ParallelWikiClassifier()
    main.process()
    print('TIME_FOR', '*'*10, 'TIMES', '*'*10)
    print('TIME_FOR', 'proc', get_conf()['general']['processes'])
    print('TIME_FOR', 'item', get_conf()['general']['item_limit'])
    for fun_name, fun_time in time_records:
        print('TIME_FOR', fun_name, int((fun_time*1000))/1000)
