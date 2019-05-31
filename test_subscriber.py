#!/usr/bin/env python
import signal
import uuid
import os
import json
import sys
import time
import logging

from distutils.util import strtobool

import paho.mqtt.client as mqtt

loglevel = os.getenv('LOGLEVEL', 'info')

logging.basicConfig(level=getattr(logging, loglevel.upper()),stream=sys.stderr)
logger = logging.getLogger(__name__)


def on_connect(client, userdata, flags, rc):
    logging.info("Connected as %s with result code %s" % (sub_name, str(rc)))
    topics = ["car/steering","car/speed"]
    for topic in topics:
        client.subscribe(topic)
        logging.info(f'Connected to {topic}')

def on_message(client, userdata, msg):
    #logging.debug(sys.getdefaultencoding())
    #logging.debug(sys.stdout.encoding)
    #logging.debug(sys.version)
    logging.info("Message Received!")
    logging.debug(msg.payload.decode('utf-8'))

def sigterm_handler(signal, frame):
    client.disconnect()
    logging.info('System shutting down, closing connection')
    sys.exit(0)

signal.signal(signal.SIGTERM, sigterm_handler)

def main():

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, port, 60)

    client.loop_start()
    time.sleep(duration)
    client.loop_stop()


if __name__ == '__main__':
    broker = os.getenv('MQTT_BROKER', 'localhost')
    port =  int(os.getenv('MQTT_PORT', 1883))
    sub_name = os.getenv('HOSTNAME', ('subscriber-' + uuid.uuid4().hex.upper()[0:6]))
    websocket = strtobool(os.getenv('MQTT_SOCKET', 'False'))
    client = mqtt.Client(sub_name)
    duration =  int(os.getenv('DURATION', 300))
    main()


# Following line is a test curl command to post a json message

 #curl --header "Content-Type: application/json" --request POST --data '{"speed":"188","steering":"12"}' http://localhost:5000/api/v1/publish/message