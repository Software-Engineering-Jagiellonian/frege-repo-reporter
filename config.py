import os

DB_HOST = os.environ['DB_HOST']
DB_PORT = int(os.environ['DB_PORT'])
DB_USER = os.environ['DB_USERNAME']
DB_PASS = os.environ['DB_PASSWORD']
DB_NAME = os.environ['DB_DATABASE']

RABBITMQ_HOST = os.environ['RMQ_HOST']
RABBITMQ_PORT = int(os.environ['RMQ_PORT'])

OUT_QUEUE_NAME = 'download'

PUBLISH_DELAY = os.environ['RMQ_REJECTED_PUBLISH_DELAY']
