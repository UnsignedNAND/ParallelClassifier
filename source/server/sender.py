#!/usr/bin/env python
import pika
import json

from utils.config_manager import get_conf
from utils.logger import get_logger
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select
from db.db import Page, Base, engine

conf = get_conf()
logger = get_logger()


def send():
    connection = None
    channel = None
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=conf['hosts']['controller']))
        channel = connection.channel()
        channel.queue_declare(queue='parse_queue', durable=True)
    except Exception as exception:
        logger.error(exception)
        exit()

    Base.metadata.bind = engine
    db_session = sessionmaker(bind=engine)
    session = db_session()

    select_all = select([Page])
    result = session.execute(select_all)

    for row in result:
        data = {
            'id': row['id'],
            'title': row['title'],
            'redirect': row['redirect'],
            'text': row['text']
        }
        message = json.dumps(data)
        channel.basic_publish(exchange='',
                              routing_key='parse_queue',
                              body=message,
                              properties=pika.BasicProperties(
                                 delivery_mode=2,  # make message persistent
                              ))
        print(" [x] Sent %r" % message)
    connection.close()
