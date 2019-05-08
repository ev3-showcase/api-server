import os
import uuid
import json
from distutils.util import strtobool
import paho.mqtt.client as mqtt
import flask
from flask import request, json

broker = os.getenv('MQTT_BROKER', 'ts.rdy.one')
port =  int(os.getenv('MQTT_PORT', 11883))
pub_name = os.getenv('HOSTNAME', ('publisher-' + uuid.uuid4().hex.upper()[0:6]))
websocket = strtobool(os.getenv('MQTT_SOCKET', 'False'))
wait_timer = int(os.getenv('MQTT_WAITTIME', 1))

if websocket:
    client = mqtt.Client(pub_name,transport='websockets')
else:
    client = mqtt.Client(pub_name)

client.connect(broker, port, 60)
client.loop_start()

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return "<h1>Car Control Communication Hub</h1><p>This site is a prototype API for an EV3 Showcase project.</p>"

@app.route('/api/v1/publish/message', methods = ['POST'])
def api_message():

    if request.headers['Content-Type'] == 'application/json':
        message = request.json
        #json.dumps(request.json)
        #message = {'speed': 0, 'steering': 0}
          
        speed_perc = message["speed"]
        client.publish('car/speed', int(speed_perc))
        angle_perc = message["steering"]
        client.publish('car/steering', int(angle_perc))
        return "Messages Sent!"

    else:
        return "415 Unsupported Media Type ;)"



# publish auf 2 topics mit int ganzahlwerten 
# car/speed
# car/steering

#validieren

#(subrout /topics (LIST/CREATE/DELETE))

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

app.run()