#!/usr/bin/env python
import pika
import time
import json

from utils.config_manager import get_conf

conf = get_conf()

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=conf['hosts']['controller']))
channel = connection.channel()

channel.queue_declare(queue='parse_queue', durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')


def callback(ch, method, properties, body):
    body = json.loads(body)
    print(" [x] Received %r" % body['id'])
    time.sleep(1)

    print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                      queue='parse_queue')

channel.start_consuming()
