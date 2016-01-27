#!/usr/bin/env python
from datetime import datetime
import pika
import socket

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost', port=5672))
channel = connection.channel()

channel.queue_declare(queue='hello')

channel.basic_publish(exchange='',
                      routing_key='hello',
                      body='Hello World! From: ' + socket.gethostname() + ' @ ' + str(datetime.now()))
print(" [x] Sent 'Hello World!'")
connection.close()
