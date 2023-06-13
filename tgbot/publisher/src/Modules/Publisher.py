import telebot
import pika
import json


class Publisher:
    def __init__(self):
        self.connect()
        self.create_channel()

    def connect(self):
        parameters = pika.URLParameters('amqp://maria:123456@rabbitmq:5672')
        self.connection = pika.BlockingConnection(parameters)

    def create_channel(self):
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='main')

    def send_message(self, params):
        self.channel.basic_publish(exchange='',
                                routing_key='main',
                                body=json.dumps(params))
        self.connection.close()
