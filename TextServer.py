from flask import Flask
from flask import request
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
import datetime
import json
import os
 
pnconfig = PNConfiguration()
pnconfig.publish_key = 'pub-c-76e8488a-fde8-47c9-ae8a-b16895b941a1'
pnconfig.subscribe_key = 'sub-c-ab4c26e4-3813-11e7-887b-02ee2ddab7fe'

pubnub = PubNub(pnconfig)
 
 
def my_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if not status.is_error():
        pass  # Message successfully published to specified channel.
    else:
        pass  # Handle message publish error. Check 'category' property to find out possible issue
        # because of which request did fail.
        # Request can be resent using: [status retry];

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/inbound')
def inbound():
    sender = request.args.get('msisdn')
    text = request.args.get('text')
    print('Sender=' + request.args.get('msisdn'))
    print('Message=' + request.args.get('text'))

    message = {"SenderType":"SMS", 'SenderId': sender, "Content": text, "TimeStamp": str(datetime.datetime.now())}
    pubnub.publish().channel("inbound").message(message).async(publish_callback)

    return ""

class MySubscribeCallback(SubscribeCallback):
    def presence(self, pubnub, presence):
        pass  # handle incoming presence data
 
    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            pass  # This event happens when radio / connectivity is lost
 
        elif status.category == PNStatusCategory.PNConnectedCategory:
            # Connect event. You can do stuff like publish, and know you'll get it.
            # Or just use the connected event to confirm you are subscribed for
            # UI / internal notifications, etc
            pass
        elif status.category == PNStatusCategory.PNReconnectedCategory:
            pass
            # Happens as part of our regular operation. This event happens when
            # radio / connectivity is lost, then regained.
        elif status.category == PNStatusCategory.PNDecryptionErrorCategory:
            pass
            # Handle message decryption error. Probably client configured to
            # encrypt messages and on live data feed it received plain text.
 
    def sendMessage(self, to, content):
        os.system('curl -X POST  https://rest.nexmo.com/sms/json -d api_key=206f2e1a -d api_secret=781c926726f53841 '+
                  '-d to='+str(to)+' -d from=12035338299 -d text="'+content+'"')

    def message(self, pubnub, message):
        print('Received over pubnub: '+ str(message.message))
        sender = message.message["SenderId"] 
        content = message.message["Content"]
        self.sendMessage(sender, content)

pubnub.add_listener(MySubscribeCallback())

def publish_callback(result, status):
    print(result)
    print(status)

def test_publish():
    print(pubnub)
    pubnub.publish().channel("inbound").message('test').async(publish_callback)

pubnub.subscribe().channels('outbound').execute()
