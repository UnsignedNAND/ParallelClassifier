#!/usr/bin/env python
import pika
import json

from process import simplify

from utils.config_manager import get_conf
from utils.logger import get_logger
from utils.timer import timer

conf = get_conf()
logger = get_logger()


@timer
def parse(text):
    simplify(text)


def receive():
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=conf['hosts']['controller']))
    channel = connection.channel()

    channel.queue_declare(queue='parse_queue', durable=True)
    logger.info(' [*] Waiting for messages. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        body = json.loads(body)
        logger.info(" [x] Received %r" % body['id'])
        parse(body['text'])
        logger.info(" [x] Done")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback,
                          queue='parse_queue')

    channel.start_consuming()
