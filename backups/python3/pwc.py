# import argparse
# from db import db
# from utils.config_manager import get_conf
# from utils.logger import get_logger
# from utils.parser import parse
#
# # from sqlalchemy.orm import sessionmaker
# # from sqlalchemy.exc import IntegrityError
#
# # from db.db import Base, engine, ProcessedPage, OccurrenceCount, \
# #     OccurrenceDocument, clean
#
# conf = get_conf()
# logger = get_logger()
#
# arg_parser = argparse.ArgumentParser(description='Parallel Wiki Classifier')
# arg_parser.add_argument('--parse', default=False, action='store_true',
#                         help='Parse Wikipedia XML dump and load it do database.')
# arg_parser.add_argument('--process', default=False, action='store_true',
#                         help='Process text documents stored in database.')
# arg_parser.add_argument('--process_receive', default=False, action='store_true',
#                         help='Process received parsed documents from remote computes.')
# arg_parser.add_argument('--clean', default=False, action='store_true',
#                         help='Delete all data from database.')
#
# args = arg_parser.parse_args()
#
#
# if not args:
#     print('Supply at least one action.')
#     arg_parser.print_help()
#     exit()
#
# if args.clean:
#     db.clean()
#
# if args.parse:
#     parse()

from db import db
from utils.config_manager import get_conf
from utils.logger import get_logger
from utils.parser import parse

conf = get_conf()
logger = get_logger()
parse()
