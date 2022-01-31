import traceback
from collections import deque
from datetime import datetime as dt

import json
import paho.mqtt.client as mqtt

DEFAULT_MQTT_SERVER = "pi-fw.local"
DEFAULT_QUEUE_LEN = 10
DEFAULT_TOPIC = "sense_hat/#"
DEAFULT_NO_OF_DECIMALS = 3

class SensorDataReader:

    def __init__(self, mq_server=DEFAULT_MQTT_SERVER, queue_len=DEFAULT_QUEUE_LEN,
                 timestamp_format="%d/%m/%Y, %H:%M:%S.%f",
                 no_of_deimals=DEAFULT_NO_OF_DECIMALS,topic=DEFAULT_TOPIC):
        self.mq_server = mq_server
        self.queue_len = queue_len
        self.no_of_decimals = no_of_deimals
        self.timestamp_format = timestamp_format
        self.simple_data_q = deque(maxlen=queue_len)
        self.accel_data_q = deque(maxlen=queue_len)
        self.gyro_data_q = deque(maxlen=queue_len)
        self.ori_data_q = deque(maxlen=queue_len)
        self.topic = topic
        self.topic_to_f_mapping = {
            "sense_hat/data/basic": self.store_simple_data,
            "sense_hat/data/accel": self.store_accel_data,
            "sense_hat/data/gyro": self.store_gyro_data,
            "sense_hat/data/orientation": self.store_orientation_data
        }

    def format_timestamp(self, ts):
        return dt.fromtimestamp(ts).strftime(self.timestamp_format)

    def round_data_points(self, data_dict):
        for k in filter(lambda x: x != "ts", data_dict.keys()):
            data_dict[k] = round(data_dict[k], self.no_of_decimals)
        return data_dict

    def store_simple_data(self, data):
        simple_data = json.loads(data)
        simple_data["ts"] = self.format_timestamp(simple_data["ts"])
        simple_data["humidity"] = simple_data["humidity"]
        simple_data["temperature_c"] = simple_data["temperature_c"]
        simple_data["pressure_millibars"] = simple_data["pressure_millibars"]
        simple_data["compass_north"] = simple_data["compass_north"]

        self.simple_data_q.append(self.round_data_points(simple_data))

    def store_accel_data(self, data):
        accel_data_dict = json.loads(data)
        accel_data = {"ts": self.format_timestamp(accel_data_dict["ts"]),
                      "roll": accel_data_dict["roll"],
                      "yaw": accel_data_dict["yaw"],
                      "pitch": accel_data_dict["pitch"],
}
        self.accel_data_q.append(self.round_data_points(accel_data))

    def store_orientation_data(self, data):
        orientation_data_dict = json.loads(data)
        orientation_data = {"ts": self.format_timestamp(orientation_data_dict["ts"]),
                            "roll": orientation_data_dict["roll"],
                            "yaw": orientation_data_dict["yaw"],
                            "pitch": orientation_data_dict["pitch"]}
        self.ori_data_q.append(self.round_data_points(orientation_data))

    def store_gyro_data(self, data):
        gyro_data_dict = json.loads(data)
        gyro_data = {"ts": self.format_timestamp(gyro_data_dict["ts"]), 
                     "roll": gyro_data_dict["roll"],
                     "yaw": gyro_data_dict["yaw"],
                     "pitch": gyro_data_dict["pitch"],
                     }
        self.gyro_data_q.append(self.round_data_points(gyro_data))

    def store_live_data(self, topic, data):
        f = self.topic_to_f_mapping.get(topic)
        if f != None:
            f(data)
        else:
            None
            # print("Unable to process data from topic " + topic)

    def init_and_start_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            print("Connected...")
            print("Subcribing to " + self.topic)
            client.subscribe(self.topic)

        def on_disconnect(client, userdata, rc):
            print("Disconnected...")

        def on_message(client, userdata, msg):
            self.store_live_data(msg.topic, msg.payload)

        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.on_disconnect = on_disconnect
        client.connect(DEFAULT_MQTT_SERVER)
        client.loop_start()
