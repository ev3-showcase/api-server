import os
import sys
import uuid
import json
import logging
from distutils.util import strtobool
from flask import Flask, request, json, Response, jsonify
from flask_ask import Ask, statement, question, session
from flask_mqtt import Mqtt

loglevel = os.getenv('LOGLEVEL', 'info')
logging.basicConfig(level=getattr(logging, loglevel.upper()),stream=sys.stderr)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET'] = 'my secret key'
app.config['MQTT_BROKER_URL'] = os.getenv('MQTT_BROKER', 'localhost')
app.config['MQTT_BROKER_PORT'] = int(os.getenv('MQTT_PORT', 1883))
app.config['MQTT_USERNAME'] = ''
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 60
app.config['MQTT_TLS_ENABLED'] = False
pub_name = os.getenv('HOSTNAME', ('publisher-' + uuid.uuid4().hex.upper()[0:6]))

mqtt = Mqtt(app)
ask = Ask(app, "/api/v1/publish/echo")
#def create_app():
#    app = flask.Flask(__name__)
#    def run_on_start(*args, **argv):
#        broker = os.getenv('MQTT_BROKER', 'ts.rdy.one')
#        port =  int(os.getenv('MQTT_PORT', 11883))
#        wait_timer = int(os.getenv('MQTT_WAITTIME', 1))
#
#        print ("Run init sequence")
#        print ("Connecting ...")
#        client.connect(broker, port, 60)
#        print ("Starting Loop...")
#        client.loop_start()
#    run_on_start()
#    return app
#app = create_app()
#app.config["DEBUG"] = True

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
        mqtt.publish('car/speed', int(speed_perc))
        angle_perc = message["steering"]
        mqtt.publish('car/steering', int(angle_perc))
        return "Messages Sent!"

    else:
        return "415 Unsupported Media Type ;)"


# publish auf 2 topics mit int ganzahlwerten 
# car/speed
# car/steering

#validieren

#(subrout /topics (LIST/CREATE/DELETE))

# ----------- Das sind die Funktionen für den Echo Skill -----------

def resolve_echo_request(echo_request):
    pass

@ask.launch
def start_skill():
    welcome_message = 'Okay. Ich starte den Motor. Du kannst jetzt losfahren.'
    return question(welcome_message)

@ask.intent("SteerIntent")
def steer_car():
    steer_message = 'Halt dich fest, jetzt geht es in die Kurve.'
    return question(steer_message)

@ask.intent("AccelerateIntent")
def accelerate_car():
    accel_msg = 'Fühlst du, wie es dich in den Sitz presst?'
    return question(accel_msg)

@ask.intent("StopCarIntent")
def stop_car():
    stopCar_msg = 'Oh, anscheinend habe ich den Motor abgewürgt.'
    return statement(stopCar_msg)

@ask.intent("StopIntent")
def stop_car():
    stop_msg = 'Okay, dann fahre ich halt allein nachhause. Tschüss'
    return statement(stop_msg)

@ask.intent("HelpIntent")
def stop_car():
    help_msg = 'Du kannst das Auto abbiegen lassen, beschleunigen und anhalten. Rede einfach mit mir.'
    return statement(help_msg)




@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

app.run(host='0.0.0.0', port=8080)


#@app.route('/api/v1/publish/echo', methods = ['POST'])
#def api_accelerate():
#    logger.info(request.headers)
#    logger.warning("Content Type:"+request.headers["Content-Type"])
#    message = request.json
#    logger.info(message)
#    
#    responsejson = {
#        "version": "1.0",
#        "response": {
#            "outputSpeech": {
#                "type": "Dein Wunsch sei mir Befehl.",
#                "text": "Dein wunsch sei mir Befehl. Brummmmmmmm",
#                "playBehavior": "REPLACE_ENQUEUED"      
#            },
#            "reprompt": {
#                "outputSpeech": {
#                    "type": "Soll ich weiterfahren?",
#                    "text": "Soll ich weiterfahren?",
#                    "playBehavior": "REPLACE_ENQUEUED"             
#                }
#            },
#            "shouldEndSession": True
#        }
#    }
#

    # do stuff

#    response = Response(response=json.dumps(responsejson), status=200, mimetype='application/json')
#    return response

    #if request.headers['Content-Type'] == 'application/json':
    #    message = request.json
    #    logger.info(message)
    #    logger.warning(message)
    #    logger.error(message)
    #    logger.info("message")
    #    logger.warning("message")
    #    logger.error("message")
    #    print(message)
    #    print("message")+



        #speed_perc = message["speed"]
        #mqtt.publish('car/speed', int(speed_perc))
        #angle_perc = message["steering"]
        #mqtt.publish('car/steering', int(angle_perc))
        #return "POST Received"

    #else:
        #logger.info("415 Unsupported Media Type ;)")
        #logger.warning("415 Unsupported Media Type ;)")
        #logger.error("415 Unsupported Media Type ;)")
        #print("415 Unsupported Media Type ;)")
        #return "415 Unsupported Media Type ;)"


# ----------- Echo Skill ende -----------