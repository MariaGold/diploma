from Modules.Callback import Callback

import pika
import json


class Consumer:
    def __init__(self):
        self.connect()
        self.get_channel()
        self.wait_messages()

    def connect(self):
        # parameters = pika.URLParameters('amqp://maria:123456@rabbitmq:5672')
        credentials = pika.PlainCredentials('maria', '123456')
        parameters = pika.ConnectionParameters(host='rabbitmq',
                                           port=5672,
                                           virtual_host='/',
                                           credentials=credentials,
                                           heartbeat=600)
        self.connection = pika.BlockingConnection(parameters)

    def get_channel(self):
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='main')

    def callback(self, ch, method, properties, body):
        params = json.loads(body)

        worker = Callback(params)
        worker.execute()

    def wait_messages(self):
        self.channel.basic_consume(on_message_callback=self.callback, queue='main', auto_ack=True)
        self.channel.start_consuming()
