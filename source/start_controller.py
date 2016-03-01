#!/usr/bin/python

import argparse
import pika
import json

from controller.parser import parse as parse_wiki
from controller.sender import send

from utils.config_manager import get_conf
from utils.logger import get_logger

from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import select

from db.db import Base, engine, ProcessedPage, OccurrenceCount, OccurrenceDocument

conf = get_conf()
logger = get_logger()

arg_parser = argparse.ArgumentParser(description='Parallel Wiki Classifier')
arg_parser.add_argument('--parse', default=False, action='store_true',
                        help='Parse Wikipedia XML dump and load it do database.')
arg_parser.add_argument('--process', default=False, action='store_true',
                        help='Process text documents stored in database.')
arg_parser.add_argument('--process_receive', default=False, action='store_true',
                        help='Process received parsed documents from remote computes.')
arg_parser.add_argument('--delete', default=False, action='store_true',
                        help='Delete all data from database upon start.')

args = arg_parser.parse_args()

print args

#if not(args.parse or args.process):
#    print 'Supply at least one action.'
#    arg_parser.print_help()
#    exit()

if args.delete:
    pass

if args.parse:
    parse_wiki()

if args.process:
    send()

if args.process_receive:
    Base.metadata.bind = engine
    db_session = sessionmaker(bind=engine)
    session = db_session()

    def receive():
        connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=conf['hosts']['controller']))
        channel = connection.channel()

        channel.queue_declare(queue='parse_return_queue', durable=True)
        logger.info(' [*] Waiting for messages. To exit press CTRL+C')

        def callback(ch, method, properties, body):
            body = json.loads(body)
            logger.info("Received %d : %r" % (body['page_id'], body['parsed_title']))

            processed_page = ProcessedPage()
            processed_page.page_id = body['page_id']
            processed_page.parsed_title = json.dumps(body['parsed_title'])
            processed_page.parsed_text = json.dumps(body['parsed_text'])

            # For TF-IDF to work, we need some words statistics
            for word in body['parsed_text'].keys():
                result_count = session.query(OccurrenceCount).filter(OccurrenceCount.name == word)
                if result_count.count() == 0:
                    occurrence = OccurrenceCount()
                    occurrence.count = body['parsed_text'][word]['count']
                    occurrence.name = word
                else:
                    occurrence = result_count.first()
                    occurrence.count += body['parsed_text'][word]['count']
                session.add(occurrence)

                session.flush()

                occurrence_document = OccurrenceDocument()
                occurrence_document.word_id = occurrence.id
                occurrence_document.document_id = body['page_id']
                session.add(occurrence_document)

            logger.debug(processed_page.parsed_title)
            logger.debug(processed_page.parsed_text)

            session.add(processed_page)
            try:
                session.commit()
            except IntegrityError as integrity_error:
                logger.error(integrity_error)
                logger.error('Database integrity error (duplicate primary key?) : {0}'.
                             format(processed_page.parsed_title))
                exit()

            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(callback,
                              queue='parse_return_queue')

        channel.start_consuming()
    receive()
