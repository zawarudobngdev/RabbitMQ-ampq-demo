import amqp


class PyAmqpLibPublisher(object):
    def __init__(self, exchange_name):
        self.exchange_name = exchange_name
        self.queue_exists = False

    def publish(self, message, routing_key):
        conn = amqp.Connection(host="127.0.0.1",
                               userid="guest",
                               password="guest",
                               virtual_host="/",
                               insist=False)
        conn.connect()

        ch = conn.channel()
        ch.exchange_declare(exchange=self.exchange_name, type="fanout", durable=False, auto_delete=False)

        msg = amqp.Message(message)
        msg.properties["content_type"] = "text/plain"
        msg.properties["delivery_mode"] = 2
        ch.basic_publish(exchange=self.exchange_name,
                         routing_key=routing_key,
                         msg=msg)
        ch.close()
        conn.close()

    def monitor(self, qname, callback):
        conn = amqp.Connection(host="127.0.0.1", userid="guest", password="guest")
        conn.connect()

        ch = conn.channel()

        if not self.queue_exists:
            ch.queue_declare(queue=qname, durable=False, exclusive=False, auto_delete=False)
            ch.queue_bind(queue=qname, exchange=self.exchange_name)
            print(f"Binding queue {qname} to exchange {self.exchange_name}")
            self.queue_exists = True

        ch.basic_consume(callback=callback, queue=qname)

        while True:
            conn.drain_events()

        conn.close()
