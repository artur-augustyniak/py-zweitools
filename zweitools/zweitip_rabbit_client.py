#!/usr/bin/env python3

import logging
import threading
import pika
import json
from typing import Callable
logger = logging.getLogger(__name__)
logging.getLogger("pika").setLevel(logging.ERROR)
logging.getLogger("pika").propagate = False


class Publisher(object):
    def __init__(self, url, bus_name):
        self.bus_name = bus_name
        self._params = pika.URLParameters(url)
        self._conn = None
        self._channel = None
        self.clean = True

    def connect(self):
        if not self._conn or self._conn.is_closed:
            self._conn = pika.BlockingConnection(self._params)
            self._channel = self._conn.channel()
            self._channel.queue_declare(queue=self.bus_name, durable=True)

    def _publish(self, msg, exc, routing_key):

        self._channel.basic_publish(exchange=exc,
                                    routing_key=routing_key,
                                    body=msg.encode())

    def publish(self, msg, routing_key):
        try:
            self._publish(msg, "", routing_key)
        except Exception:
            if self.clean:
                self.clean = False
                logger.info("initial connection to %s ." %
                            self.bus_name)
            else:
                logger.info("reconnecting to %s in 10 sec." %
                            self.bus_name)
                time.sleep(10)
            logging.info('reconnecting to %s' % (self.bus_name))
            self.connect()
            self._publish(msg, "", routing_key)

    def close(self):
        if self._conn and self._conn.is_open:
            logging.info('closing %s' % (self.bus_name))
            self._conn.close()


class QueueWriter(object):

    def __init__(self,
                 rabbit_url: str,
                 target_queue: str
                 ) -> None:
        self.target_queue = target_queue
        self.lock = threading.RLock()
        self.publisher = Publisher(
            rabbit_url, target_queue)

    def push_message(self, event: dict) -> None:
        def nonblock_postpone():
            self.lock.acquire()
            try:
                self.publisher.publish(
                    json.dumps(event, default=str),
                    self.target_queue
                )
            finally:
                self.lock.release()
        d = threading.Thread(name="rabbit-event-emmiter",
                             target=nonblock_postpone)
        d.daemon = True
        d.start()


class ZrabbitClient(object):

    def __init__(self,
                 rabbit_url: str,
                 source_queue: str,
                 source_topic: str,
                 target_queue: str,
                 target_topic: str,
                 ):
        self.rabbit_url = rabbit_url
        self.source_queue = source_queue
        self.queue_writer = QueueWriter(
            rabbit_url,
            target_queue
        )

    def enqueue(self, event: dict, msg: str) -> None:
        event['msg'] = msg
        self.queue_writer.push_message(event)

    def blocking_queue_consume(self, handlers_decsr: dict) -> None:

        def get_event_clbk_with(handlers: dict) -> Callable:
            def clbk(ch, method, properties, body):
                try:
                    event = json.loads(body.decode('utf-8'))
                    event_key = event.get('event_name', 'nx_key')
                    handler = handlers.get(event_key)
                    if handler is not None:
                        handler.handle(event)
                    else:
                        msg = "event %s not processed in %s queue contect - no matching handler" % (
                            event_key, self.source_queue)
                        self.enqueue(event, msg)
                        logger.warning(msg)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    tb = traceback.format_exc()
                    logger.critical(
                        "force shutdown nack msg - event not processed with exception %s TB:(%s) DATA (%s)" % (
                            str(e),
                            repr(tb),
                            repr(body))
                    )
                    ch.basic_nack(delivery_tag=method.delivery_tag)
                    raise e
            return clbk

        params = pika.URLParameters(self.rabbit_url)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(self.source_queue, durable=True)

        channel.basic_consume(
            queue=self.source_queue,
            on_message_callback=get_event_clbk_with(handlers_decsr),
            auto_ack=False
        )
        channel.start_consuming()


if __name__ == '__main__':
    logger.critical("This is not the main module")
