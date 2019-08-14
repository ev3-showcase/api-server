#!/usr/bin/env python
import signal
import uuid
import os
import json
import sys
import time

from time import sleep
from distutils.util import strtobool

import paho.mqtt.client as mqtt

def count():
    for i in range(0,3):
        print (i)
        sleep(1)

def on_connect(client, userdata, flags, rc):
    print("Connected as %s with result code %s" % (sub_name, str(rc)))
    client.subscribe("car/steering")
    print("Connected to car/steering")
    client.subscribe("car/speed")
    print("Connected to car/speed")

def on_message(client, userdata, msg):
    #print(sys.getdefaultencoding())
    #print(sys.stdout.encoding)
    #print(sys.version)
    print("Message!")
    message = msg.payload.decode('utf-8')
    print(message)
    count()
    

def sigterm_handler(signal, frame):
    client.disconnect()
    print('System shutting down, closing connection')
    sys.exit(0)

signal.signal(signal.SIGTERM, sigterm_handler)



def main():

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, port, 60) 

    '''print("Starting loop now")
    client.loop_forever()'''

    client.loop_start()
    print("Loop Startet. Now waiting 600 Seconds for messages")
    time.sleep(600)
    print("Time over, bye.")
    client.loop_stop()


if __name__ == '__main__':
    broker = os.getenv('MQTT_BROKER', 'message-broker-mqtt-websocket-fk-sc.aotp012.mcs-paas.io')
    port =  int(os.getenv('MQTT_PORT', 80))
    sub_name = os.getenv('HOSTNAME', ('subscriber-' + uuid.uuid4().hex.upper()[0:6]))
    websocket = strtobool(os.getenv('MQTT_SOCKET', 'True'))
    client = mqtt.Client(sub_name,transport='websockets')
    main()


# Following line is a test curl command to post a json message

 #curl --header "Content-Type: application/json" --request POST --data '{"speed":"188","steering":"12"}' http://localhost:5000/api/v1/publish/message