#!/usr/bin/env python
import json

import pika

from compute.preprocessing.process_text import simplify
from utils.config_manager import get_conf
from utils.logger import get_logger
from utils.timer import timer

conf = get_conf()
logger = get_logger()


@timer
def parse(text, filtering=True):
    return simplify(text, filtering=filtering)


def receive():
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=conf['hosts']['controller']))
    channel = connection.channel()

    channel.queue_declare(queue='parse_queue', durable=True)
    logger.info(' [*] Waiting for messages. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        body = json.loads(body)
        logger.info("Received %d : %r" % (body['id'], body['title']))

        parsed_page = {
            'page_id': body['id'],
            'parsed_title': parse(body['title'], filtering=False),
            'parsed_text': parse(body['text']),
        }

        logger.debug("Parsed title: {0}\n"
                     "Parsed text: {1}".
                     format(parsed_page['parsed_title'],
                            parsed_page['parsed_text']))

        channel.basic_publish(exchange='',
                              routing_key='parse_return_queue',
                              body=json.dumps(parsed_page),
                              properties=pika.BasicProperties(
                                 delivery_mode=2,  # make message persistent
                              ))
        logger.info("Parsed and responded.")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback,
                          queue='parse_queue')

    channel.start_consuming()
