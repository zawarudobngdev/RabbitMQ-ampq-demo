import pika


class PikaPublisher(object):
    def __init__(self, exchange_name):
        self.exchange_name = exchange_name
        self.queue_exists = False

    def publish(self, message, routing_key):
        conn = pika.SelectConnection(pika.ConnectionParameters(
            '127.0.0.1',
            credentials=pika.PlainCredentials('guest', 'guest')))

        ch = conn.channel()

        ch.exchange_declare(exchange=self.exchange_name, exchange_type="fanout", durable=False, auto_delete=False)

        ch.basic_publish(exchange=self.exchange_name,
                         routing_key=routing_key,
                         body=message,
                         properties=pika.BasicProperties(
                             content_type="text/plain",
                             delivery_mode=2,  # persistent
                         ),
                         )
        ch.close()
        conn.close()

    def monitor(self, qname, callback):
        conn = pika.SelectConnection(pika.ConnectionParameters(
            '127.0.0.1',
            credentials=pika.PlainCredentials('guest', 'guest')))

        ch = conn.channel()

        if not self.queue_exists:
            ch.queue_declare(queue=qname, durable=False, exclusive=False, auto_delete=False)
            ch.queue_bind(queue=qname, exchange=self.exchange_name)
            print(f"Binding queue {qname} to exchange {self.exchange_name}")
            # ch.queue_bind(queue=qname, exchange=self.exchange_name, routing_key=qname)
            self.queue_exists = True

        ch.basic_consume(qname, callback)

        try:
            # Loop so we can communicate with RabbitMQ
            conn.ioloop.start()
        except KeyboardInterrupt:
            # Gracefully close the connection
            conn.close()
            # Loop until we're fully closed.
            # The on_close callback is required to stop the io loop
            conn.ioloop.start()
