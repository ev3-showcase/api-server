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
        if "speed" in message.keys():
            speed_perc = message["speed"]
            mqtt.publish('car/speed', int(speed_perc))
        if "steering" in message.keys():
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



@ask.launch
def start_skill():
    welcome_message = 'Okay. Ich starte den Motor. Du kannst jetzt losfahren.'
    return question(welcome_message)

@ask.intent("SteerIntent", default={'angle': 'None', 'direction': 'None'})
def steer_car(angle, direction):
    
    tight_angle = ["scharf", "stark", "hart", "eng"]
    wide_angle = ["leicht", "weit", "etwas", "seicht", "ein bisschen", "bisschen"]
    left_dir = ["links", "links rum", "linker hand","left"]
    right_dir = ["rechts", "rechts rum", "rechter hand" "right"]
    steer_input = 60

    if angle in tight_angle:
        steer_input = 90
    elif angle in wide_angle:
        steer_input = 30
    else:
        pass
    
    if direction in left_dir:
        angle_perc = steer_input * -1
        mqtt.publish('car/steering', angle_perc)
        logger.info(f"Steering: {angle_perc}")
        msg_val = "nach links"
    elif direction in right_dir:
        angle_perc = steer_input
        mqtt.publish('car/steering', angle_perc)
        logger.info(f"Steering: {angle_perc}")
        msg_val = "nach rechts"
    else:
        logger.error(f"Invalid Values for Intent: angle: {angle}, direction: {direction}")
        msg_val = "überhaupt nicht"

    
    logger.info(f"angle: {angle}")
    logger.info(f"direction: {direction}")
    steer_message = f'Halt dich fest, jetzt geht es {msg_val} in die Kurve.'
    return question(steer_message)

@ask.intent("AccelerateIntent", default={'accelerationdirection': 'None', 'speed': 'None', 'speedvalue': 'None'})
def accelerate_car(accelerationdirection,speed,speedvalue):

    forward = ["vorwärts", "nach vorne", "los", "forward"]
    backward = ["rückwärts", "nach hinten", "zurück", "backward"]
    slow = ["gemach", "etwas", "gemächlich", "ruhig", "langsam"]
    fast = ["schnell", "mit karacho", "ratzfatz", "richtig", "richtig schnell"]
    speed_val = 0

    if speedvalue != 'None':
        speed_val = int(speedvalue)
        accelerationdirection = "los"
    else:
        if speed in fast:
            speed_val = 90
        elif speed in slow:
            speed_val = 30
        else:
            speed_val = 60

    if accelerationdirection in backward:
        speed_perc = speed_val * -1
        mqtt.publish('car/speed', speed_perc)
        logger.info(f"Speed: {speed_perc}")
        if speed_val >= 50:
            msg_val = "Fühlst du, wie es dich aus dem Sitz hebt?"
        else: 
            msg_val = "Siehst du einen Baum im Rückspiegel? Dann halt lieber an."
    elif accelerationdirection in forward:
        speed_perc = speed_val
        mqtt.publish('car/speed', speed_perc)
        logger.info(f"Speed: {speed_perc}")
        if speed_val >= 50:
            msg_val = "Fühlst du, wie es dich in den Sitz presst?"
        else: 
            msg_val = "Sieh nur, wie wir dahingleiten."
    else:
        logger.error(f"Invalid Values for Intent: accelerationdirection: {accelerationdirection}, speed: {speed}, speedvalue: {speedvalue}")
        msg_val = "Fühlst du, wie sich überhaupt nichts bewegt?"

    logger.info(f"accelerationdirection: {accelerationdirection}")
    logger.info(f"speed: {speed}")
    logger.info(f"speedvalue: {speedvalue}")
    accel_msg = msg_val
    return question(accel_msg)

@ask.intent("StopCarIntent")
def stop_car():
    mqtt.publish('car/speed', 0)
    mqtt.publish('car/steering', 0)
    logger.info("Stopping Car")
    stopCar_msg = 'Oh, anscheinend habe ich den Motor abgewürgt. Was soll ich nun tun?'
    return question(stopCar_msg)

@ask.intent("StraightIntent")
def straighten_car():
    mqtt.publish('car/steering', 0)
    logger.info("Straighten Steering for Car")
    straightCar_msg = 'Okay... Wir sind wieder auf Kurs.'
    return question(straightCar_msg)

@ask.intent("AMAZON.StopIntent")
def stop_car():
    mqtt.publish('car/speed', 0)
    mqtt.publish('car/steering', 0)
    logger.info("Stopping Car")
    stop_msg = 'Okay, dann fahre ich halt allein nachhause. Tschüss'
    return statement(stop_msg)

@ask.intent("AMAZON.HelpIntent")
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