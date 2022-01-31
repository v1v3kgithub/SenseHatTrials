# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import paho.mqtt.client as mqtt
from datetime import datetime
import json



def on_connect(client,userdata,flags,rc):
    print("Connected...")
    client.subscribe("sense_hat/data")

def on_message(client,userdata,msg):
    ts = datetime.fromtimestamp(msg.timestamp).strftime('%Y-%m-%d:%')
    print(msg.topic + " : " + str(msg.payload) + " : " + ts)
    print(json.loads(msg.payload)["humidity"])



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("192.168.0.175")
    client.loop_forever()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
