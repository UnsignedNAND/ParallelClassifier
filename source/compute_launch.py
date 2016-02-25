#!/usr/bin/env python
import pika
from utils.config_manager import get_conf

conf = get_conf()

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=conf['hosts']['controller']))
channel = connection.channel()

channel.queue_declare(queue='hello')


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)

channel.basic_consume(callback,
                      queue='hello',
                      no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
