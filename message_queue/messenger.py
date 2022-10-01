import json
import time
import pika

from config import RABBITMQ_HOST, RABBITMQ_PORT, OUT_QUEUE_NAME, PUBLISH_DELAY


def _connect():
    return pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT))


def send_message_to_downloader(message):
    with _connect() as connection:
        _output_channel = connection.channel()
        _output_channel.confirm_delivery()
        _output_channel.queue_declare(queue=OUT_QUEUE_NAME, durable=True)

        while True:
            # List of queues to retry sending
            retry = False
            try:
                print(f"Sending message to {OUT_QUEUE_NAME}...")
                _output_channel.basic_publish(
                    exchange='',
                    routing_key=OUT_QUEUE_NAME,
                    properties=pika.BasicProperties(delivery_mode=2,),
                    body=bytes(json.dumps(message), encoding='utf8')
                )
                print("Output message received by RabbitMQ")
            except pika.exceptions.NackError as e:
                print(f"Output message NACK from RabbitMQ (queue full). Retrying in {PUBLISH_DELAY} s")
                retry = True
            # If the queues to retry list is not empty
            if retry:
                time.sleep(PUBLISH_DELAY)
            else:
                break
